"""Utilitaires pour l'application core."""

from django.utils import timezone


def log_activity(
    user,
    action,
    model_name="",
    object_id=None,
    object_repr="",
    details="",
    ip_address=None,
):
    """
    Enregistre une action dans le journal d'activité (ActivityLog).
    
    Args:
        user: L'utilisateur ayant effectué l'action (peut être None)
        action: Le type d'action (create, update, delete, login, logout, order_status, other)
        model_name: Nom du modèle concerné
        object_id: ID de l'objet concerné
        object_repr: Représentation textuelle de l'objet
        details: Détails supplémentaires
        ip_address: Adresse IP de l'utilisateur
    """
    from .models import ActivityLog

    ActivityLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=model_name,
        object_id=object_id,
        object_repr=object_repr,
        details=details,
        ip_address=ip_address,
    )