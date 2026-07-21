from django.db import models


class SiteConfiguration(models.Model):
    """Configuration générale du site modifiable depuis l'administration."""

    # Identité
    site_name = models.CharField(max_length=120, default="CVB Store", verbose_name="Nom du site")
    site_tagline = models.CharField(
        max_length=255,
        default="Votre boutique moderne pour commander rapidement en ligne.",
        verbose_name="Slogan",
    )
    logo = models.ImageField(upload_to="branding/", blank=True, null=True, verbose_name="Logo")
    favicon = models.ImageField(
        upload_to="branding/", blank=True, null=True, verbose_name="Favicon",
        help_text="Icône du site (format .ico ou .png, 32x32px recommandé)",
    )

    # Hero de la page d'accueil (fallback si pas de bannières)
    hero_title = models.CharField(
        max_length=150,
        default="Commandez vos produits en quelques clics",
        verbose_name="Titre du hero",
    )
    hero_subtitle = models.TextField(
        default=(
            "Une boutique rapide, claire et professionnelle avec panier dynamique, "
            "catégories organisées et commande simplifiée."
        ),
        verbose_name="Sous-titre du hero",
    )

    # Page À propos
    about_title = models.CharField(max_length=150, default="À propos de nous", verbose_name="Titre À propos")
    about_content = models.TextField(
        default=(
            "Personnalisez cette section depuis l'administration pour présenter "
            "votre entreprise, vos valeurs et vos engagements."
        ),
        verbose_name="Contenu À propos",
    )
    about_image = models.ImageField(
        upload_to="branding/", blank=True, null=True, verbose_name="Image À propos"
    )

    # Contact
    contact_phone = models.CharField(max_length=40, blank=True, verbose_name="Téléphone")
    contact_email = models.EmailField(blank=True, verbose_name="Email de contact")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse physique")

    # Horaires
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name="Horaires d'ouverture",
        help_text="Exemple: Lun-Ven: 8h-18h, Sam: 9h-14h",
    )

    # Réseaux sociaux
    whatsapp_url = models.URLField(blank=True, verbose_name="WhatsApp")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    telegram_url = models.URLField(blank=True, verbose_name="Telegram")
    tiktok_url = models.URLField(blank=True, verbose_name="TikTok")

    # SEO
    meta_description = models.TextField(
        blank=True, verbose_name="Meta description globale (SEO)",
        help_text="Description du site pour les moteurs de recherche",
    )
    meta_keywords = models.CharField(
        max_length=255, blank=True, verbose_name="Mots-clés SEO",
        help_text="Séparés par des virgules",
    )

    # Personnalisation
    primary_color = models.CharField(
        max_length=7, default="#0d6efd", verbose_name="Couleur primaire",
        help_text="Code hexadécimal ex: #0d6efd",
    )
    secondary_color = models.CharField(
        max_length=7, default="#6c757d", verbose_name="Couleur secondaire",
    )

    # Footer
    footer_text = models.TextField(
        blank=True, verbose_name="Texte du pied de page",
        help_text="Copyright, mentions légales...",
    )

    # Métadonnées
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


class ContactMessage(models.Model):
    """Message envoyé depuis le formulaire de contact."""

    name = models.CharField(max_length=150, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    replied = models.BooleanField(default=False, verbose_name="Répondu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Reçu le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.name} - {self.subject}"


class FAQ(models.Model):
    """Question fréquemment posée."""

    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class PageContent(models.Model):
    """Page statique (CGV, confidentialité, etc.)."""

    SLUG_CHOICES = [
        ("cgv", "Conditions générales de vente"),
        ("privacy", "Politique de confidentialité"),
        ("legal", "Mentions légales"),
        ("delivery", "Livraison et retours"),
    ]

    slug = models.SlugField(
        max_length=50, unique=True, choices=SLUG_CHOICES,
        verbose_name="Type de page",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"

    def __str__(self):
        return self.get_slug_display()