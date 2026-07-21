from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from catalog.models import Banner, Category, Product
from orders.models import Order

from .forms import (
    BannerForm,
    CategoryForm,
    DashboardAuthenticationForm,
    ProductForm,
)


def _staff_check(user):
    return user.is_authenticated and user.is_staff


staff_required = user_passes_test(_staff_check, login_url=reverse_lazy("dashboard:login"))


class DashboardLoginView(LoginView):
    form_class = DashboardAuthenticationForm
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("dashboard:index")


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard:login")


# ===== DASHBOARD HOME =====

@staff_required
def dashboard_home(request):
    orders = Order.objects.all()
    product_count = Product.objects.count()
    category_count = Category.objects.count()
    active_product_count = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(stock__lte=5, is_active=True).count()
    featured_count = Product.objects.filter(is_featured=True, is_active=True).count()
    on_sale_count = Product.objects.filter(on_sale=True, is_active=True).count()
    banner_count = Banner.objects.filter(is_active=True).count()
    total_revenue = orders.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

    status_breakdown = {
        "pending": orders.filter(status=Order.STATUS_PENDING).count(),
        "confirmed": orders.filter(status=Order.STATUS_CONFIRMED).count(),
        "preparing": orders.filter(status=Order.STATUS_PREPARING).count(),
        "delivered": orders.filter(status=Order.STATUS_DELIVERED).count(),
        "cancelled": orders.filter(status=Order.STATUS_CANCELLED).count(),
    }

    recent_orders = orders.prefetch_related("items").order_by("-created_at")[:6]
    top_products = (
        Product.objects.filter(order_items__isnull=False)
        .select_related("category")
        .annotate(
            sold_quantity=Sum("order_items__quantity"),
            order_count=Count("order_items__order", distinct=True),
        )
        .order_by("-sold_quantity", "name")[:5]
    )
    low_stock_products = Product.objects.filter(
        is_active=True, stock__lte=5
    ).order_by("stock", "name")[:5]

    context = {
        "stats": {
            "order_count": orders.count(),
            "product_count": product_count,
            "category_count": category_count,
            "active_product_count": active_product_count,
            "low_stock_count": low_stock_count,
            "featured_count": featured_count,
            "on_sale_count": on_sale_count,
            "banner_count": banner_count,
            "customer_count": orders.values("email").exclude(email="").distinct().count(),
            "revenue": total_revenue,
        },
        "status_breakdown": status_breakdown,
        "recent_orders": recent_orders,
        "top_products": top_products,
        "low_stock_products": low_stock_products,
    }
    return render(request, "dashboard/index.html", context)


# ===== PRODUCTS =====

@staff_required
def product_list(request):
    q = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    products = Product.objects.select_related("category").order_by("-is_featured", "name")

    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(short_description__icontains=q)
            | Q(sku__icontains=q)
        )
    if category_filter and category_filter.isdigit():
        products = products.filter(category_id=int(category_filter))
    if status_filter == "active":
        products = products.filter(is_active=True)
    elif status_filter == "inactive":
        products = products.filter(is_active=False)
    elif status_filter == "featured":
        products = products.filter(is_featured=True)
    elif status_filter == "on_sale":
        products = products.filter(on_sale=True)
    elif status_filter == "low_stock":
        products = products.filter(stock__lte=5, is_active=True)

    categories = Category.objects.filter(is_active=True)

    context = {
        "products": products,
        "categories": categories,
        "summary": {
            "total": Product.objects.count(),
            "active": Product.objects.filter(is_active=True).count(),
            "featured": Product.objects.filter(is_featured=True).count(),
            "on_sale": Product.objects.filter(on_sale=True).count(),
        },
    }
    return render(request, "dashboard/product_list.html", context)


@staff_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Produit « {product.name} » créé avec succès.")
            return redirect("dashboard:product_list")
    else:
        form = ProductForm()

    return render(request, "dashboard/product_form.html", {"form": form})


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Produit « {product.name} » modifié.")
            return redirect("dashboard:product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "dashboard/product_form.html", {"form": form})


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Produit « {name} » supprimé.")
        return redirect("dashboard:product_list")
    return render(request, "dashboard/confirm_delete.html", {
        "object": product,
        "cancel_url": reverse_lazy("dashboard:product_list"),
    })


# ===== CATEGORIES =====

@staff_required
def category_list(request):
    q = request.GET.get("q", "").strip()

    categories = Category.objects.annotate(
        product_total=Count("products", distinct=True),
        active_product_total=Count(
            "products", filter=Q(products__is_active=True), distinct=True
        ),
    ).order_by("name")

    if q:
        categories = categories.filter(name__icontains=q)

    context = {
        "categories": categories,
        "summary": {
            "total": categories.count(),
            "active": categories.filter(is_active=True).count(),
            "inactive": categories.filter(is_active=False).count(),
        },
    }
    return render(request, "dashboard/category_list.html", context)


@staff_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Catégorie « {category.name} » créée.")
            return redirect("dashboard:category_list")
    else:
        form = CategoryForm()

    return render(request, "dashboard/category_form.html", {"form": form})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Catégorie « {category.name} » modifiée.")
            return redirect("dashboard:category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "dashboard/category_form.html", {"form": form})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = category.name
        category.delete()
        messages.success(request, f"Catégorie « {name} » supprimée.")
        return redirect("dashboard:category_list")
    return render(request, "dashboard/confirm_delete.html", {
        "object": category,
        "cancel_url": reverse_lazy("dashboard:category_list"),
    })


# ===== ORDERS =====

@staff_required
def order_list(request):
    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    orders = Order.objects.annotate(item_count=Count("items")).order_by("-created_at")

    if q:
        orders = orders.filter(
            Q(full_name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
            | Q(id__icontains=q)
        )
    if status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)

    context = {
        "orders": orders,
        "status_choices": Order.STATUS_CHOICES,
        "summary": {
            "total": orders.count(),
            "pending": orders.filter(status=Order.STATUS_PENDING).count(),
            "confirmed": orders.filter(status=Order.STATUS_CONFIRMED).count(),
            "delivered": orders.filter(status=Order.STATUS_DELIVERED).count(),
        },
    }
    return render(request, "dashboard/order_list.html", context)


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"), pk=pk
    )

    if request.method == "POST" and request.POST.get("action") == "update_status":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=["status", "updated_at"])
            messages.success(
                request,
                f"Commande # {order.id} : statut mis à jour → {order.get_status_display()}.",
            )
        return redirect("dashboard:order_detail", pk=order.pk)

    context = {
        "order": order,
        "status_choices": Order.STATUS_CHOICES,
    }
    return render(request, "dashboard/order_detail.html", context)


# ===== BANNERS =====

@staff_required
def banner_list(request):
    banners = Banner.objects.all().order_by("position", "order", "-created_at")
    context = {
        "banners": banners,
        "summary": {
            "total": banners.count(),
            "active": banners.filter(is_active=True).count(),
            "hero": banners.filter(position="hero").count(),
        },
    }
    return render(request, "dashboard/banner_list.html", context)


@staff_required
def banner_create(request):
    if request.method == "POST":
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, f"Bannière « {banner.title or 'Sans titre'} » créée.")
            return redirect("dashboard:banner_list")
    else:
        form = BannerForm()

    return render(request, "dashboard/banner_form.html", {"form": form, "title": "Nouvelle bannière"})


@staff_required
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == "POST":
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, f"Bannière « {banner.title or 'Sans titre'} » modifiée.")
            return redirect("dashboard:banner_list")
    else:
        form = BannerForm(instance=banner)

    return render(request, "dashboard/banner_form.html", {"form": form, "title": "Modifier la bannière"})


@staff_required
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == "POST":
        title = banner.title or "Sans titre"
        banner.delete()
        messages.success(request, f"Bannière « {title} » supprimée.")
        return redirect("dashboard:banner_list")
    return render(request, "dashboard/confirm_delete.html", {
        "object": banner,
        "cancel_url": reverse_lazy("dashboard:banner_list"),
    })