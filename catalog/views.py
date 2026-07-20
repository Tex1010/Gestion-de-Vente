from django.shortcuts import get_object_or_404, render

from .models import Product


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )
    related_products = (
        Product.objects.filter(
            category=product.category,
            is_active=True,
        )
        .exclude(pk=product.pk)[:4]
    )
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )
