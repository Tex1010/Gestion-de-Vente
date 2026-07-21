from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request, category_slug=None):
    """Page catalogue avec filtres, tri et pagination."""
    selected_category = request.GET.get("categorie", "").strip()
    search_term = request.GET.get("q", "").strip()
    sort_by = request.GET.get("tri", "-created_at")
    min_price = request.GET.get("prix_min", "").strip()
    max_price = request.GET.get("prix_max", "").strip()

    # Catégorie spécifique (via URL)
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = Product.objects.filter(
            category=category, is_active=True, category__is_active=True
        )
    else:
        products = Product.objects.filter(is_active=True, category__is_active=True)

    products = products.select_related("category")

    # Filtre par nom
    if search_term:
        products = products.filter(
            Q(name__icontains=search_term)
            | Q(short_description__icontains=search_term)
            | Q(description__icontains=search_term)
        )

    # Filtre par catégorie (via GET)
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Filtre par prix
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Tri
    valid_sort_options = {
        "price": "price",
        "-price": "-price",
        "name": "name",
        "-name": "-name",
        "created_at": "created_at",
        "-created_at": "-created_at",
    }
    ordering = valid_sort_options.get(sort_by, "-created_at")
    products = products.order_by(ordering)

    # Catégories pour les filtres
    categories = Category.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "products",
            queryset=Product.objects.filter(is_active=True),
        )
    )

    context = {
        "category": category,
        "products": products,
        "categories": categories,
        "search_term": search_term,
        "selected_category": selected_category,
        "current_sort": sort_by,
        "min_price": min_price,
        "max_price": max_price,
    }
    return render(request, "catalog/product_list.html", context)


def product_detail(request, slug):
    """Page détail d'un produit avec galerie, variantes et suggestions."""
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related(
            "images", "variants"
        ),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    # Produits similaires (même catégorie, exclus celui-ci)
    similar_products = (
        Product.objects.filter(
            category=product.category,
            is_active=True,
        )
        .exclude(pk=product.pk)
        .select_related("category")[:4]
    )

    # Récupérer la première image de la galerie si elle existe pour le meta
    primary_image = product.images.filter(is_primary=True).first()
    gallery_images = product.images.all()

    context = {
        "product": product,
        "similar_products": similar_products,
        "primary_image": primary_image,
        "gallery_images": gallery_images,
    }
    return render(request, "catalog/product_detail.html", context)