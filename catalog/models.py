from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(
        upload_to="categories/", blank=True, null=True, verbose_name="Image"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        ordering = ["name"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Catégorie",
    )
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(
        max_length=255, blank=True, verbose_name="Description courte"
    )
    description = models.TextField(blank=True, verbose_name="Description détaillée")

    # Prix et promotion
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Prix actuel"
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ancien prix",
    )
    on_sale = models.BooleanField(default=False, verbose_name="En promotion")

    # Stock et référence
    sku = models.CharField(
        max_length=80, unique=True, blank=True, null=True, verbose_name="SKU"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")

    # Physique
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Poids (kg)",
        help_text="Poids du produit en kilogrammes",
    )
    dimensions = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Dimensions",
        help_text="Exemple : 30 x 20 x 15 cm",
    )

    # Image principale
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="Image principale"
    )

    # SEO
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="Meta title (SEO)",
        help_text="Titre pour les moteurs de recherche (70 caractères max)",
    )
    meta_description = models.CharField(
        max_length=165,
        blank=True,
        verbose_name="Meta description (SEO)",
        help_text="Description pour les moteurs de recherche (165 caractères max)",
    )

    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_featured = models.BooleanField(default=False, verbose_name="Produit vedette")

    # Datas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        ordering = ["-is_featured", "name"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:200]
            self.slug = base_slug
            # Assurer l'unicité du slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        """Retourne True si le produit a une réduction active."""
        return bool(self.old_price and self.old_price > self.price)


class ProductImage(models.Model):
    """Images supplémentaires d'un produit (galerie)."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Produit",
    )
    image = models.ImageField(
        upload_to="products/gallery/", verbose_name="Image"
    )
    alt_text = models.CharField(
        max_length=150, blank=True, verbose_name="Texte alternatif",
        help_text="Description de l'image pour l'accessibilité et le SEO",
    )
    is_primary = models.BooleanField(
        default=False, verbose_name="Image principale"
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = "Image du produit"
        verbose_name_plural = "Images du produit"

    def __str__(self):
        return f"Image {self.order} - {self.product.name}"

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule image principale
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True)\
                .exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """Variante d'un produit (taille, couleur, etc.)."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="Produit",
    )
    name = models.CharField(
        max_length=100, verbose_name="Nom de la variante",
        help_text="Exemple: 'Taille M', 'Couleur Rouge'",
    )
    sku = models.CharField(
        max_length=80, unique=True, blank=True, null=True, verbose_name="SKU variante"
    )
    price_adjustment = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        verbose_name="Ajustement de prix",
        help_text="Montant à ajouter ou soustraire (ex: -500 pour -5,00 €)",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock de la variante")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class Banner(models.Model):
    """Bannière publicitaire / Slider de la page d'accueil."""

    POSITION_CHOICES = [
        ("hero", "Hero principal (grande bannière)"),
        ("secondary", "Secondaire (bannière plus petite)"),
    ]

    title = models.CharField(
        max_length=200, blank=True, verbose_name="Titre"
    )
    subtitle = models.TextField(
        blank=True, verbose_name="Sous-titre"
    )
    image = models.ImageField(
        upload_to="banners/", verbose_name="Image de la bannière"
    )
    link_url = models.URLField(
        blank=True, verbose_name="Lien",
        help_text="URL de destination quand on clique sur la bannière",
    )
    link_text = models.CharField(
        max_length=80, blank=True, verbose_name="Texte du bouton",
        help_text="Exemple: 'Voir la collection'",
    )
    position = models.CharField(
        max_length=20, choices=POSITION_CHOICES, default="hero",
        verbose_name="Position",
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "order", "created_at"]
        verbose_name = "Bannière / Slider"
        verbose_name_plural = "Bannières / Sliders"

    def __str__(self):
        return self.title or f"Bannière {self.pk}"