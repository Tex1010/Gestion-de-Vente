from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from catalog.models import Banner, Category, Product, ProductImage, ProductVariant
from core.models import SiteConfiguration


class DashboardAuthenticationForm(AuthenticationForm):
    """Restrict dashboard access to staff users."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                "Cette interface est réservée aux administrateurs et gestionnaires.",
                code="not_staff",
            )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "short_description",
            "description",
            "price",
            "old_price",
            "on_sale",
            "sku",
            "stock",
            "weight",
            "dimensions",
            "image",
            "meta_title",
            "meta_description",
            "is_active",
            "is_featured",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select", "required": True}),
            "name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "short_description": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 255}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "required": True}
            ),
            "old_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "on_sale": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "weight": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": 0}
            ),
            "dimensions": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "30 x 20 x 15 cm",
                }
            ),
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "meta_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 70,
                    "placeholder": "Titre SEO (70 car.)",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "maxlength": 165,
                    "placeholder": "Description SEO (165 car.)",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_sku(self):
        sku = self.cleaned_data.get("sku")
        if not sku:
            return sku
        # Vérifier unicité du SKU (en excluant l'instance actuelle)
        qs = Product.objects.filter(sku=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ce SKU est déjà utilisé par un autre produit.")
        return sku


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "is_primary", "order"]
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*", "required": True}
            ),
            "alt_text": forms.TextInput(attrs={"class": "form-control"}),
            "is_primary": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ["name", "sku", "price_adjustment", "stock", "is_active", "order"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "placeholder": "Ex: Taille M",
                }
            ),
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "price_adjustment": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "+0.00",
                }
            ),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "image", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            "title",
            "subtitle",
            "image",
            "link_url",
            "link_text",
            "position",
            "is_active",
            "order",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "subtitle": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*", "required": True}
            ),
            "link_url": forms.URLInput(attrs={"class": "form-control"}),
            "link_text": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            # Identité
            "site_name",
            "site_tagline",
            "logo",
            "favicon",
            # Hero
            "hero_title",
            "hero_subtitle",
            # À propos
            "about_title",
            "about_content",
            "about_image",
            # Contact
            "contact_phone",
            "contact_email",
            "address",
            "opening_hours",
            # Réseaux sociaux / raccourcis
            "whatsapp_url",
            "facebook_url",
            "instagram_url",
            "telegram_url",
            "tiktok_url",
            # SEO
            "meta_description",
            "meta_keywords",
            # Couleurs
            "primary_color",
            "secondary_color",
            # Footer
            "footer_text",
        ]
        widgets = {
            "site_name": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "site_tagline": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "favicon": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "hero_title": forms.TextInput(attrs={"class": "form-control"}),
            "hero_subtitle": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "about_title": forms.TextInput(attrs={"class": "form-control"}),
            "about_content": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "about_image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "opening_hours": forms.TextInput(attrs={"class": "form-control"}),
            "whatsapp_url": forms.URLInput(attrs={"class": "form-control"}),
            "facebook_url": forms.URLInput(attrs={"class": "form-control"}),
            "instagram_url": forms.URLInput(attrs={"class": "form-control"}),
            "telegram_url": forms.URLInput(attrs={"class": "form-control"}),
            "tiktok_url": forms.URLInput(attrs={"class": "form-control"}),
            "meta_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "meta_keywords": forms.TextInput(attrs={"class": "form-control"}),
            "primary_color": forms.TextInput(attrs={"class": "form-control", "placeholder": "#0d6efd"}),
            "secondary_color": forms.TextInput(attrs={"class": "form-control", "placeholder": "#6c757d"}),
            "footer_text": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
