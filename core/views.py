from django.db.models import Prefetch, Q
from django.shortcuts import render

from catalog.models import Category, Product
from .models import SiteConfiguration


def home(request):
    selected_category = request.GET.get("categorie", "").strip()
    search_term = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True, category__is_active=True).select_related(
        "category"
    )
    if selected_category:
        products = products.filter(category__slug=selected_category)
    if search_term:
        products = products.filter(
            Q(name__icontains=search_term)
            | Q(short_description__icontains=search_term)
            | Q(description__icontains=search_term)
        )

    categories = Category.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "products",
            queryset=Product.objects.filter(is_active=True).order_by("-is_featured", "name"),
        )
    )

    context = {
        "site_config": SiteConfiguration.load(),
        "categories": categories,
        "featured_products": Product.objects.filter(
            is_active=True,
            is_featured=True,
            category__is_active=True,
        )[:6],
        "products": products,
        "selected_category": selected_category,
        "search_term": search_term,
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(
        request,
        "core/about.html",
        {"site_config": SiteConfiguration.load()},
    )
