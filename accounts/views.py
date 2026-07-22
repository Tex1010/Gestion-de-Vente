import secrets
import string
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from catalog.models import Product
from orders.models import Order

from .forms import (
    AddToWishlistForm,
    LoginForm,
    RegistrationForm,
    UserInfoForm,
    UserProfileForm,
)
from .models import PasswordResetRequest, UserProfile, Wishlist


def register_view(request):
    """Inscription d'un nouveau client."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique après inscription
            raw_password = form.cleaned_data.get("password1")
            user_auth = authenticate(
                request, username=user.username, password=raw_password
            )
            if user_auth:
                login(request, user_auth)
            messages.success(
                request,
                f"Bienvenue {user.username} ! Votre compte a été créé avec succès.",
            )
            return redirect("core:home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Connexion d'un client."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bon retour {user.username} !")
            next_url = request.GET.get("next", "core:home")
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Déconnexion complète (client + dashboard). Redirige vers la page de connexion client."""
    # Supprimer le flag dashboard s'il existe
    if "_dashboard_authenticated_user_id" in request.session:
        del request.session["_dashboard_authenticated_user_id"]
        request.session.modified = True
    # Déconnexion totale Django (vide toute la session)
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    """Page du profil utilisateur."""
    profile = request.user.profile

    if request.method == "POST":
        # Déterminer quel formulaire est soumis
        if "update_profile" in request.POST:
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=profile
            )
            user_form = UserInfoForm(request.POST, instance=request.user)
            if profile_form.is_valid() and user_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Votre profil a été mis à jour.")
                return redirect("accounts:profile")
        elif "change_password" in request.POST:
            # Rediriger vers la page de changement de mot de passe Django
            return redirect("accounts:password_change")
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    # Commandes de l'utilisateur
    orders = Order.objects.filter(email=request.user.email).order_by("-created_at")[:10]
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("product")

    context = {
        "profile_form": profile_form,
        "user_form": user_form,
        "orders": orders,
        "wishlist_items": wishlist_items,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def order_history(request):
    """Historique des commandes de l'utilisateur."""
    orders = Order.objects.filter(email=request.user.email).order_by("-created_at")
    return render(request, "accounts/order_history.html", {"orders": orders})


@login_required
def wishlist_view(request):
    """Liste des favoris de l'utilisateur."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("product")

    if request.method == "POST":
        form = AddToWishlistForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data["product_id"]
            product = get_object_or_404(Product, pk=product_id, is_active=True)

            # Ajouter ou retirer des favoris (toggle)
            wish_item = Wishlist.objects.filter(
                user=request.user, product=product
            ).first()
            if wish_item:
                wish_item.delete()
                messages.info(
                    request, f"« {product.name} » retiré de vos favoris."
                )
            else:
                Wishlist.objects.create(user=request.user, product=product)
                messages.success(
                    request, f"« {product.name} » ajouté à vos favoris."
                )
            return redirect(request.POST.get("next", "accounts:wishlist"))

    return render(
        request, "accounts/wishlist.html", {"wishlist_items": wishlist_items}
    )


def password_reset_request_view(request):
    """Page où le client entre son email pour demander un nouveau mot de passe."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Veuillez entrer votre adresse email.")
            return render(request, "accounts/password_reset.html")

        # Vérifier si l'email existe dans la base de données
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(
                request,
                "Aucun compte associé à cette adresse email. "
                "Veuillez vérifier votre saisie ou créer un compte.",
            )
            return render(request, "accounts/password_reset.html")

        # Vérifier qu'il n'y a pas déjà une demande en attente pour cet email
        pending = PasswordResetRequest.objects.filter(
            email=email, is_resolved=False
        ).exists()

        if pending:
            messages.info(
                request,
                "Une demande est déjà en attente pour cet email. "
                "Un administrateur la traitera bientôt.",
            )
        else:
            # Créer la demande
            PasswordResetRequest.objects.create(
                email=email,
                user=user,
            )
            messages.success(
                request,
                "Votre demande a été envoyée à l'administrateur. "
                "Vous recevrez un email avec votre nouveau mot de passe une fois traitée.",
            )

        return redirect("accounts:password_reset_done")

    return render(request, "accounts/password_reset.html")


def password_reset_done_view(request):
    """Page de confirmation après l'envoi de la demande."""
    return render(request, "accounts/password_reset_done.html")


def generate_random_password(length=12):
    """Génère un mot de passe aléatoire sécurisé."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))