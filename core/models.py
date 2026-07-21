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


class Coupon(models.Model):
    """Code promotionnel / Coupon de réduction."""

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Pourcentage (%)"),
        ("fixed", "Montant fixe (Ar)"),
    ]

    code = models.CharField(
        max_length=50, unique=True, verbose_name="Code du coupon",
        help_text="Code saisi par le client (ex: PROMO10)",
    )
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPE_CHOICES, default="percentage",
        verbose_name="Type de réduction",
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valeur de la réduction",
        help_text="Pourcentage (ex: 10 pour 10%) ou montant fixe en Ar",
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Montant minimum de commande",
    )
    max_uses = models.PositiveIntegerField(
        default=0, verbose_name="Utilisations max",
        help_text="0 = illimité",
    )
    current_uses = models.PositiveIntegerField(
        default=0, verbose_name="Utilisations actuelles",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    valid_from = models.DateTimeField(verbose_name="Valable du")
    valid_to = models.DateTimeField(verbose_name="Valable au")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Coupon de réduction"
        verbose_name_plural = "Coupons de réduction"

    def __str__(self):
        return f"{self.code} (-{self.discount_value}{'%' if self.discount_type == 'percentage' else ' Ar'})"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.current_uses >= self.max_uses:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True

    def apply_discount(self, total):
        """Calcule le montant après réduction."""
        from decimal import Decimal
        if self.discount_type == "percentage":
            discount = total * (self.discount_value / Decimal("100"))
        else:
            discount = self.discount_value
        return max(total - discount, Decimal("0.00"))

    def get_discount_amount(self, total):
        """Calcule le montant de la réduction."""
        from decimal import Decimal
        if self.discount_type == "percentage":
            return total * (self.discount_value / Decimal("100"))
        return self.discount_value


class ShippingZone(models.Model):
    """Zone de livraison avec frais associés."""

    name = models.CharField(
        max_length=120, verbose_name="Nom de la zone",
        help_text="Exemple: Antananarivo, Province, Nationale",
    )
    cities = models.TextField(
        blank=True, verbose_name="Villes concernées",
        help_text="Liste des villes séparées par des virgules",
    )
    base_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Frais de base",
    )
    free_shipping_min = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name="Livraison offerte à partir de (Ar)",
        help_text="Montant minimum pour livraison gratuite. Laissez vide pour désactiver.",
    )
    estimated_days = models.CharField(
        max_length=80, blank=True, verbose_name="Délai estimé",
        help_text="Exemple: 2-3 jours ouvrés",
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"

    def __str__(self):
        return self.name


class TaxRate(models.Model):
    """Taux de taxe (TVA, etc.)."""

    name = models.CharField(
        max_length=80, verbose_name="Nom",
        help_text="Exemple: TVA 20%, TVA réduite 5.5%",
    )
    rate = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Taux (%)",
        help_text="Exemple: 20 pour 20%",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_default = models.BooleanField(
        default=False, verbose_name="Par défaut",
        help_text="Sera appliqué automatiquement aux commandes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-rate"]
        verbose_name = "Taux de taxe"
        verbose_name_plural = "Taux de taxe"

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

    def apply(self, amount):
        """Calcule le montant de la taxe pour un montant donné."""
        from decimal import Decimal
        return amount * (self.rate / Decimal("100"))


class PaymentMethod(models.Model):
    """Mode de paiement en ligne."""

    METHOD_CHOICES = [
        ("mvola", "Mvola"),
        ("airtel_money", "Airtel Money"),
        ("orange_money", "Orange Money"),
    ]

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        unique=True,
        verbose_name="Méthode de paiement",
    )
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["method"]
        verbose_name = "Mode de paiement"
        verbose_name_plural = "Modes de paiement"

    def __str__(self):
        return f"{self.get_method_display()} - {self.phone_number}"


class ActivityLog(models.Model):
    """Journal des actions effectuées dans l'administration."""

    ACTION_CHOICES = [
        ("create", "Création"),
        ("update", "Modification"),
        ("delete", "Suppression"),
        ("login", "Connexion"),
        ("logout", "Déconnexion"),
        ("order_status", "Changement de statut commande"),
        ("other", "Autre"),
    ]

    user = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Utilisateur",
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, default="other",
        verbose_name="Action",
    )
    model_name = models.CharField(
        max_length=100, blank=True, verbose_name="Modèle concerné",
    )
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="ID objet")
    object_repr = models.CharField(
        max_length=255, blank=True, verbose_name="Représentation",
    )
    details = models.TextField(blank=True, verbose_name="Détails")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activités"

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
