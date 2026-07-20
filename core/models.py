from django.db import models


class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=120, default="CVB Store")
    site_tagline = models.CharField(
        max_length=255,
        default="Votre boutique moderne pour commander rapidement en ligne.",
    )
    hero_title = models.CharField(
        max_length=150,
        default="Commandez vos produits en quelques clics",
    )
    hero_subtitle = models.TextField(
        default=(
            "Une boutique rapide, claire et professionnelle avec panier dynamique, "
            "catégories organisées et commande simplifiée."
        )
    )
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    about_title = models.CharField(max_length=150, default="A propos de nous")
    about_content = models.TextField(
        default=(
            "Personnalisez cette section depuis l'administration pour présenter "
            "votre entreprise, vos valeurs et vos engagements."
        )
    )
    contact_phone = models.CharField(max_length=40, blank=True)
    whatsapp_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configuration du site"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
