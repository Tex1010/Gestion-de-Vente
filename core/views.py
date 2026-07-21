from django.contrib import messages
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Banner, Category, Product
from .models import ContactMessage, FAQ, PageContent, SiteConfiguration


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

    hero_banners = Banner.objects.filter(is_active=True, position="hero").order_by("order")
    secondary_banners = Banner.objects.filter(is_active=True, position="secondary").order_by("order")

    sale_products = Product.objects.filter(
        is_active=True, on_sale=True, category__is_active=True
    ).select_related("category")[:6]

    featured_products = Product.objects.filter(
        is_active=True, is_featured=True, category__is_active=True,
    ).select_related("category")[:6]

    new_products = Product.objects.filter(
        is_active=True, category__is_active=True
    ).select_related("category").order_by("-created_at")[:6]

    context = {
        "site_config": SiteConfiguration.load(),
        "categories": categories,
        "featured_products": featured_products,
        "sale_products": sale_products,
        "new_products": new_products,
        "products": products,
        "selected_category": selected_category,
        "search_term": search_term,
        "hero_banners": hero_banners,
        "secondary_banners": secondary_banners,
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(
        request,
        "core/about.html",
        {"site_config": SiteConfiguration.load()},
    )


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message_text
            )
            messages.success(
                request,
                "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.",
            )
            return redirect("core:contact")
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")

    return render(
        request,
        "core/contact.html",
        {"site_config": SiteConfiguration.load()},
    )


def faq(request):
    faqs = FAQ.objects.filter(is_active=True).order_by("order")
    return render(
        request,
        "core/faq.html",
        {"faqs": faqs, "site_config": SiteConfiguration.load()},
    )


def page_detail(request, slug):
    """Affiche une page statique (CGV, confidentialité, etc.)."""
    page = get_object_or_404(PageContent, slug=slug, is_active=True)
    return render(
        request,
        "core/page_detail.html",
        {"page": page, "site_config": SiteConfiguration.load()},
    )