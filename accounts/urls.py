from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    login_view,
    logout_view,
    order_history,
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
    path(
        "mot-de-passe-oublie/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="done/",
        ),
        name="password_reset",
    ),
    path(
        "mot-de-passe-oublie/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reinitialiser/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/compte/reinitialiser/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reinitialiser/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]