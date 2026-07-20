from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


def _parse_quantity(raw_value):
    try:
        return max(int(raw_value), 1)
    except (TypeError, ValueError):
        return 1


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
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if product.stock <= 0:
        messages.error(request, f"{product.name} est actuellement en rupture de stock.")
        return redirect(request.POST.get("next") or "core:home")
    quantity = _parse_quantity(request.POST.get("quantity", 1))
    Cart(request).add(product=product, quantity=quantity)
    messages.success(request, f"{product.name} a ete ajoute au panier.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if product.stock <= 0:
        Cart(request).remove(product)
        messages.error(request, f"{product.name} n'est plus disponible.")
        return redirect("orders:cart_detail")
    quantity = _parse_quantity(request.POST.get("quantity", 1))
    Cart(request).add(product=product, quantity=quantity, override_quantity=True)
    messages.success(request, f"Quantite mise a jour pour {product.name}.")
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product)
    messages.info(request, f"{product.name} a ete retire du panier.")
    return redirect("orders:cart_detail")


def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)
    if not cart_items:
        messages.warning(request, "Votre panier est vide.")
        return redirect("core:home")

    stock_issues = []
    for item in cart_items:
        product = get_object_or_404(Product, pk=item["product_id"], is_active=True)
        if product.stock < item["quantity"]:
            stock_issues.append(product.name)

    if stock_issues:
        messages.warning(
            request,
            "Le stock a change pour : " + ", ".join(stock_issues) + ". Merci de verifier votre panier.",
        )
        return redirect("orders:cart_detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = Order.objects.create(**form.cleaned_data)
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item["product_id"])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=item["quantity"],
                        unit_price=product.price,
                    )
                    product.stock = max(product.stock - item["quantity"], 0)
                    product.save(update_fields=["stock"])
                order.recalculate_total()
                cart.clear()
            messages.success(request, "Votre commande a ete enregistree avec succes.")
            return redirect("orders:order_success", order_id=order.pk)
    else:
        form = CheckoutForm()

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart": cart_items,
            "cart_total": cart.get_total_price(),
        },
    )


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "orders/order_success.html", {"order": order})
