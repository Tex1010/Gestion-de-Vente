from decimal import Decimal

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from catalog.models import Category, Product
from orders.models import Order

from .forms import DashboardAuthenticationForm


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


@staff_required
def dashboard_home(request):
    orders = Order.objects.all()
    product_count = Product.objects.count()
    category_count = Category.objects.count()
    active_product_count = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(stock__lte=5, is_active=True).count()
    featured_count = Product.objects.filter(is_featured=True, is_active=True).count()
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
    low_stock_products = Product.objects.filter(is_active=True, stock__lte=5).order_by("stock", "name")[:5]

    context = {
        "stats": {
            "order_count": orders.count(),
            "product_count": product_count,
            "category_count": category_count,
            "active_product_count": active_product_count,
            "low_stock_count": low_stock_count,
            "featured_count": featured_count,
            "customer_count": orders.values("email").exclude(email="").distinct().count(),
            "revenue": total_revenue,
        },
        "status_breakdown": status_breakdown,
        "recent_orders": recent_orders,
        "top_products": top_products,
        "low_stock_products": low_stock_products,
    }
    return render(request, "dashboard/index.html", context)


@staff_required
def product_list(request):
    products = Product.objects.select_related("category").order_by("-is_featured", "name")
    context = {
        "products": products,
        "summary": {
            "total": products.count(),
            "active": products.filter(is_active=True).count(),
            "featured": products.filter(is_featured=True).count(),
            "on_sale": products.filter(old_price__isnull=False).count(),
        },
    }
    return render(request, "dashboard/product_list.html", context)


@staff_required
def category_list(request):
    categories = Category.objects.annotate(
        product_total=Count("products", distinct=True),
        active_product_total=Count("products", filter=Q(products__is_active=True), distinct=True),
    ).order_by("name")
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
def order_list(request):
    orders = Order.objects.annotate(item_count=Count("items")).order_by("-created_at")
    context = {
        "orders": orders,
        "summary": {
            "total": orders.count(),
            "pending": orders.filter(status=Order.STATUS_PENDING).count(),
            "confirmed": orders.filter(status=Order.STATUS_CONFIRMED).count(),
            "delivered": orders.filter(status=Order.STATUS_DELIVERED).count(),
        },
    }
    return render(request, "dashboard/order_list.html", context)
