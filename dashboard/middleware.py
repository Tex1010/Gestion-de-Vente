"""
Middleware pour sessions séparées entre dashboard et site public.

Permet à un admin d'être connecté au dashboard (/dashboard/)
pendant qu'un client est connecté (ou pas) sur le site public,
même depuis le même navigateur.

Fonctionnement :
- Pour /dashboard/ : cookie session = sessionid_dashboard, path = /dashboard/
- Pour le reste : cookie session = sessionid, path = /
- Les deux cookies coexistent sans s'écraser
- Ajoute aussi des en-têtes Cache-Control pour empêcher l'accès
  aux pages protégées après déconnexion via le bouton Retour
"""

from django.conf import settings
from django.utils.cache import add_never_cache_headers


class SeparateDashboardSession:
    """
    Utilise des cookies de session différents selon le chemin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard/"):
            settings.SESSION_COOKIE_NAME = "sessionid_dashboard"
            settings.SESSION_COOKIE_PATH = "/dashboard/"
            settings.CSRF_COOKIE_NAME = "csrftoken_dashboard"
            settings.CSRF_COOKIE_PATH = "/dashboard/"
        else:
            settings.SESSION_COOKIE_NAME = "sessionid"
            settings.SESSION_COOKIE_PATH = "/"
            settings.CSRF_COOKIE_NAME = "csrftoken"
            settings.CSRF_COOKIE_PATH = "/"

        response = self.get_response(request)

        # Ajouter des en-têtes anti-cache pour les pages protégées
        if request.user.is_authenticated:
            # Ne pas mettre en cache les pages authentifiées
            add_never_cache_headers(response)

        # Restaurer les valeurs par défaut
        settings.SESSION_COOKIE_NAME = "sessionid"
        settings.SESSION_COOKIE_PATH = "/"
        settings.CSRF_COOKIE_NAME = "csrftoken"
        settings.CSRF_COOKIE_PATH = "/"

        return response


class NoCacheStaffMiddleware:
    """
    Ajoute des en-têtes Cache-Control: no-cache pour les pages protégées
    afin d'empêcher le navigateur de les mettre en cache.
    Après une déconnexion, le bouton Retour ne pourra plus afficher
    les pages protégées.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ne pas mettre en cache les pages d'admin/dashboard
        if request.path.startswith("/dashboard/"):
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        # Ne pas mettre en cache les pages de compte client quand connecté
        if request.path.startswith("/compte/") and request.user.is_authenticated:
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        # Ne pas mettre en cache les pages de checkout/panier/commande
        if any(p in request.path for p in ["/panier/", "/commande/"]) and request.user.is_authenticated:
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        return response
