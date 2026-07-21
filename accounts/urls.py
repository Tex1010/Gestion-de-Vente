from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    login_view,
    logout_view,
    order_history,
    password_reset_done_view,
    password_reset_request_view,
    profile_view,
    register_view,
    wishlist_view,
)

app_name = "accounts"

urlpatterns = [
    # Auth
    path("inscription/", register_view, name="register"),
    path("connexion/", login_view, name="login"),
    path("deconnexion/", logout_view, name="logout"),
    # Profil
    path("profil/", profile_view, name="profile"),
    path("commandes/", order_history, name="order_history"),
    path("favoris/", wishlist_view, name="wishlist"),
    # Mot de passe (vues Django intégrées)
    path(
        "mot-de-passe/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="done/",
        ),
        name="password_change",
    ),
    path(
        "mot-de-passe/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    # Mot de passe oublié - approbation admin
    path(
        "mot-de-passe-oublie/",
        password_reset_request_view,
        name="password_reset",
    ),
    path(
        "mot-de-passe-oublie/envoye/",
        password_reset_done_view,
        name="password_reset_done",
    ),
]