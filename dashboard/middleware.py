"""
Middleware pour sessions séparées entre dashboard et site public.

Permet à un admin d'être connecté au dashboard (/dashboard/)
pendant qu'un client est connecté (ou pas) sur le site public,
même depuis le même navigateur.

Fonctionnement :
- Pour /dashboard/ : cookie session = sessionid_dashboard, path = /dashboard/
- Pour le reste : cookie session = sessionid, path = /
- Les deux cookies coexistent sans s'écraser
"""

from django.conf import settings


class SeparateDashboardSession:
    """
    Utilise des cookies de session différents selon le chemin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard/"):
            settings.SESSION_COOKIE_NAME = "sessionid_dashboard"
            settings.CSRF_COOKIE_NAME = "csrftoken_dashboard"
        else:
            settings.SESSION_COOKIE_NAME = "sessionid"
            settings.CSRF_COOKIE_NAME = "csrftoken"

        response = self.get_response(request)

        # Restaurer les valeurs par défaut
        settings.SESSION_COOKIE_NAME = "sessionid"
        settings.CSRF_COOKIE_NAME = "csrftoken"

        return response