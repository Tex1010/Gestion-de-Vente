"""
Middleware pour la sécurisation du dashboard et la séparation
des sessions client / administration.

Principe :
- Session unique Django (cookie `sessionid` unique)
- L'authentification dashboard utilise un indicateur
  `_dashboard_authenticated_user_id` stocké dans la session
- Dashboard logout : supprime UNIQUEMENT cet indicateur,
  l'utilisateur reste connecté sur le site client
- Client logout (Django standard) : vide toute la session,
  ce qui supprime aussi l'indicateur dashboard
- En-têtes Cache-Control systématiques sur toutes les pages protégées
  pour empêcher l'accès via le bouton Retour après déconnexion
"""

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class DashboardAuthMiddleware(MiddlewareMixin):
    """
    Vérifie que l'utilisateur accédant au dashboard possède
    l'indicateur `_dashboard_authenticated_user_id` dans sa session.

    Sans cet indicateur, même un staff ne peut pas accéder au dashboard :
    il est redirigé vers la page de connexion dashboard.
    """

    def process_request(self, request):
        if not request.path.startswith("/dashboard/"):
            return None

        # Pages autorisées sans authentification dashboard
        allowed_paths = (
            "/dashboard/login/",
            "/dashboard/logout/",
        )
        if any(request.path.startswith(p) for p in allowed_paths):
            return None

        # Vérifier la présence de l'indicateur dashboard dans la session
        dashboard_uid = request.session.get("_dashboard_authenticated_user_id")
        if not dashboard_uid:
            return redirect(reverse("dashboard:login"))

        # Vérifier que l'utilisateur connecté correspond bien
        if not request.user.is_authenticated or request.user.id != dashboard_uid:
            return redirect(reverse("dashboard:login"))

        # Vérifier que c'est bien un staff
        if not request.user.is_staff:
            return redirect(reverse("dashboard:login"))

        return None


class NoCacheProtectedPagesMiddleware(MiddlewareMixin):
    """
    Ajoute des en-têtes HTTP anti-cache pour empêcher le navigateur
    de conserver en cache les pages protégées.

    Après une déconnexion, le bouton Retour du navigateur ne pourra
    plus afficher les pages protégées : l'utilisateur sera redirigé
    vers la page de connexion correspondante.
    """

    PROTECTED_PREFIXES = (
        "/dashboard/",
        "/compte/",
        "/panier/",
        "/commande/",
    )

    def process_response(self, request, response):
        # Vérifier si l'URL est protégée
        path = request.path
        is_protected = any(path.startswith(p) for p in self.PROTECTED_PREFIXES)

        # Également protéger si l'utilisateur est authentifié
        # (pages qui ne sont pas dans les préfixes mais nécessitent une session)
        if is_protected or (hasattr(request, "user") and request.user.is_authenticated):
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        return response