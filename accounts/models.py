from django.contrib.auth.models import User
from django.db import models

from catalog.models import Product


class UserProfile(models.Model):
    """Profil utilisateur étendu."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=40, blank=True, verbose_name="Téléphone")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=120, blank=True, verbose_name="Ville")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Photo de profil"
    )
    birth_date = models.DateField(
        blank=True, null=True, verbose_name="Date de naissance"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.username}"


class Wishlist(models.Model):
    """Liste de souhaits / Favoris d'un utilisateur."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlists"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ["user", "product"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class PasswordResetRequest(models.Model):
    """Demande de réinitialisation de mot de passe (approuvée par l'admin)."""

    email = models.EmailField(verbose_name="Email du demandeur")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Utilisateur associé",
        help_text="Rempli automatiquement si l'email correspond à un compte.",
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Demandé le")
    is_resolved = models.BooleanField(default=False, verbose_name="Résolue")
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name="Résolue le")
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="password_resets_handled",
        verbose_name="Traitée par",
    )
    new_password = models.CharField(
        max_length=128, blank=True,
        verbose_name="Nouveau mot de passe généré",
    )

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Demande de réinitialisation"
        verbose_name_plural = "Demandes de réinitialisation"

    def __str__(self):
        return f"{self.email} - {self.requested_at.strftime('%d/%m/%Y %H:%M')}"


# Signal pour créer automatiquement le profil à l'inscription
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()