from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from catalog.models import Product, ProductVariant

from core.models import PaymentMethod, ShippingZone
from core.utils import log_activity

from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


def _parse_quantity(raw_value):
    try:
        return max(int(raw_value), 1)
    except (TypeError, ValueError):
        return 1


def _get_variant(product, raw_variant_id):
    if not raw_variant_id:
        return None
    return get_object_or_404(
        ProductVariant,
        pk=raw_variant_id,
        product=product,
        is_active=True,
    )


def _get_user_order_queryset(user):
    filters = Q(user=user)
    if user.email:
        filters |= Q(user__isnull=True, email=user.email)
    return Order.objects.filter(filters)


def cart_detail(request):
    cart = Cart(request)
    return render(
        request,
        "orders/cart.html",
        {
            "cart": list(cart),
            "cart_total": cart.get_total_price(),
        },
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related("variants"),
        pk=product_id,
        is_active=True,
    )
    variant = _get_variant(product, request.POST.get("variant_id"))

    has_selectable_variants = product.variants.filter(is_active=True, stock__gt=0).exists()
    if has_selectable_variants and variant is None:
        messages.info(
            request,
            "Veuillez choisir une variante avant d'ajouter ce produit au panier.",
        )
        return redirect("catalog:product_detail", slug=product.slug)

    available_stock = variant.stock if variant else product.stock
    if available_stock <= 0:
        messages.error(request, f"{product.name} est actuellement en rupture de stock.")
        return redirect(request.POST.get("next") or "catalog:product_detail", slug=product.slug)

    quantity = _parse_quantity(request.POST.get("quantity", 1))
    Cart(request).add(product=product, quantity=quantity, variant=variant)
    if variant:
        messages.success(request, f"{product.name} ({variant.name}) a ete ajoute au panier.")
    else:
        messages.success(request, f"{product.name} a ete ajoute au panier.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def cart_update(request, item_key):
    cart = Cart(request)
    item = cart.cart.get(item_key)
    if not item:
        messages.warning(request, "Cet article n'est plus dans votre panier.")
        return redirect("orders:cart_detail")

    product = get_object_or_404(Product, pk=item["product_id"], is_active=True)
    variant = _get_variant(product, item.get("variant_id"))
    available_stock = variant.stock if variant else product.stock
    if available_stock <= 0:
        cart.remove(item_key)
        messages.error(request, f"{product.name} n'est plus disponible.")
        return redirect("orders:cart_detail")

    quantity = _parse_quantity(request.POST.get("quantity", 1))
    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=True,
        variant=variant,
    )
    if variant:
        messages.success(request, f"Quantite mise a jour pour {product.name} ({variant.name}).")
    else:
        messages.success(request, f"Quantite mise a jour pour {product.name}.")
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, item_key):
    cart = Cart(request)
    item = cart.cart.get(item_key)
    if not item:
        messages.warning(request, "Cet article n'est plus dans votre panier.")
        return redirect("orders:cart_detail")

    product = get_object_or_404(Product, pk=item["product_id"])
    variant = _get_variant(product, item.get("variant_id"))
    cart.remove(item_key)
    if variant:
        messages.info(request, f"{product.name} ({variant.name}) a ete retire du panier.")
    else:
        messages.info(request, f"{product.name} a ete retire du panier.")
    return redirect("orders:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)
    if not cart_items:
        messages.warning(request, "Votre panier est vide.")
        return redirect("core:home")

    stock_issues = []
    for item in cart_items:
        product = get_object_or_404(Product, pk=item["product_id"], is_active=True)
        variant = _get_variant(product, item.get("variant_id"))
        available_stock = variant.stock if variant else product.stock
        if available_stock < item["quantity"]:
            label = f"{product.name} ({variant.name})" if variant else product.name
            stock_issues.append(label)

    if stock_issues:
        messages.warning(
            request,
            "Le stock a change pour : " + ", ".join(stock_issues) + ". Merci de verifier votre panier.",
        )
        return redirect("orders:cart_detail")

    cart_subtotal = cart.get_total_price()
    shipping_zones = ShippingZone.objects.filter(is_active=True).order_by("order", "name")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            payment_method_key = form.cleaned_data["payment_method"]
            delivery_method = form.cleaned_data["delivery_method"]
            shipping_zone_id = form.cleaned_data.get("shipping_zone", "")
            shipping_cost = Decimal("0.00")
            shipping_zone_name = ""

            # Calculer les frais de livraison si livraison
            if delivery_method == Order.DELIVERY_SHIP and shipping_zone_id:
                try:
                    zone = ShippingZone.objects.get(pk=int(shipping_zone_id), is_active=True)
                    shipping_cost = zone.base_cost
                    shipping_zone_name = zone.name
                except (ShippingZone.DoesNotExist, ValueError, TypeError):
                    shipping_cost = Decimal("0.00")
                    shipping_zone_name = ""

            # Récupérer le numéro marchand
            payment_phone = ""
            try:
                payment_method_obj = PaymentMethod.objects.get(
                    method=payment_method_key, is_active=True
                )
                payment_phone = payment_method_obj.phone_number
            except PaymentMethod.DoesNotExist:
                pass

            client_payment_phone = form.cleaned_data.get("client_payment_phone", "")

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    email=form.cleaned_data["email"],
                    city=form.cleaned_data.get("city", ""),
                    address=form.cleaned_data.get("address", ""),
                    notes=form.cleaned_data.get("notes", ""),
                    delivery_method=delivery_method,
                    shipping_zone_name=shipping_zone_name,
                    shipping_cost=shipping_cost,
                    payment_method=payment_method_key,
                    payment_phone=payment_phone,
                    payment_reference=form.cleaned_data["payment_reference"],
                )

                # Stocker le numéro client dans les notes
                if client_payment_phone:
                    note = f"Numéro d'envoi du paiement : {client_payment_phone}"
                    if order.notes:
                        order.notes = order.notes + f"\n\n{note}"
                    else:
                        order.notes = note

                # Créer les items
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item["product_id"])
                    variant = None
                    if item.get("variant_id"):
                        variant = ProductVariant.objects.select_for_update().get(
                            pk=item["variant_id"],
                            product=product,
                            is_active=True,
                        )
                    unit_price = variant.effective_price if variant else product.price
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        product_name=product.name,
                        variant_name=variant.name if variant else "",
                        quantity=item["quantity"],
                        unit_price=unit_price,
                    )
                    if variant:
                        variant.stock = max(variant.stock - item["quantity"], 0)
                        variant.save(update_fields=["stock"])
                    product.stock = max(product.stock - item["quantity"], 0)
                    product.save(update_fields=["stock"])

                # Utiliser recalculate_total qui inclut les frais de livraison
                order.recalculate_total()

                # Mettre à jour les notes
                if order.notes:
                    Order.objects.filter(pk=order.pk).update(notes=order.notes)

                cart.clear()

            log_activity(
                request.user, "create", "Commande", order.pk, f"Commande #{order.pk}",
                f"Nouvelle commande #{order.pk} - {form.cleaned_data['full_name']} - "
                f"Total: {order.total_amount} Ar - "
                f"Réception: {'Livraison' if delivery_method == 'ship' else 'Retrait'} - "
                f"Paiement: {payment_method_key}",
                request.META.get("REMOTE_ADDR"),
            )

            messages.success(request, "Votre commande a ete enregistree avec succes.")
            return redirect("orders:order_success", order_id=order.pk)
    else:
        initial = {
            "full_name": request.user.get_full_name() or request.user.username,
            "phone": getattr(request.user.profile, "phone", ""),
            "email": request.user.email,
            "city": getattr(request.user.profile, "city", ""),
            "address": getattr(request.user.profile, "address", ""),
            "delivery_method": "pickup",
        }
        form = CheckoutForm(initial=initial)

    payment_methods = PaymentMethod.objects.filter(is_active=True)

    # Construire les données des zones de livraison pour le frontend JSON
    shipping_zones_json = {
        str(zone.pk): {
            "cost": float(zone.base_cost),
            "name": zone.name,
        }
        for zone in shipping_zones
    }

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart": cart_items,
            "cart_total": cart_subtotal,
            "payment_methods": payment_methods,
            "shipping_zones": shipping_zones,
            "shipping_zones_json": shipping_zones_json,
        },
    )


@login_required
def order_success(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order.objects.prefetch_related("items__variant"), pk=order_id)
    else:
        order = get_object_or_404(
            _get_user_order_queryset(request.user).prefetch_related("items__variant"),
            pk=order_id,
        )
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def cancel_order(request, order_id):
    """Permet au client d'annuler une commande si elle est encore en attente."""
    order = get_object_or_404(
        _get_user_order_queryset(request.user),
        pk=order_id,
    )
    if order.status != Order.STATUS_PENDING:
        messages.error(request, "Cette commande ne peut plus être annulée.")
        return redirect("orders:order_success", order_id=order.pk)

    with transaction.atomic():
        # Restaurer le stock
        for item in order.items.select_for_update().select_related("product", "variant"):
            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save(update_fields=["stock"])
            item.product.stock += item.quantity
            item.product.save(update_fields=["stock"])

        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=["status", "updated_at"])

    messages.success(request, f"Votre commande #{order.id} a été annulée.")
    return redirect("orders:order_success", order_id=order.pk)