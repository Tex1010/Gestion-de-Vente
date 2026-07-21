from django.contrib import admin

from .models import (
    ActivityLog,
    ContactMessage,
    Coupon,
    FAQ,
    PageContent,
    PaymentMethod,
    ShippingZone,
    SiteConfiguration,
    TaxRate,
)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Identité", {
            "fields": ["site_name", "site_tagline", "logo", "favicon"]
        }),
        ("Page d'accueil (fallback)", {
            "fields": ["hero_title", "hero_subtitle"]
        }),
        ("Page À propos", {
            "fields": ["about_title", "about_content", "about_image"]
        }),
        ("Contact", {
            "fields": ["contact_phone", "contact_email", "address", "opening_hours"]
        }),
        ("Réseaux sociaux", {
            "fields": ["whatsapp_url", "facebook_url", "instagram_url", "telegram_url", "tiktok_url"]
        }),
        ("SEO", {
            "fields": ["meta_description", "meta_keywords"],
            "classes": ["collapse"]
        }),
        ("Personnalisation", {
            "fields": ["primary_color", "secondary_color", "footer_text"],
            "classes": ["collapse"]
        }),
    ]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "subject", "email", "is_read", "replied", "created_at"]
    list_filter = ["is_read", "replied"]
    search_fields = ["name", "email", "subject", "message"]
    list_editable = ["is_read", "replied"]
    readonly_fields = ["created_at"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["question"]


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_active", "updated_at"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "is_active", "valid_from", "valid_to", "current_uses", "max_uses"]
    list_filter = ["is_active", "discount_type"]
    search_fields = ["code"]
    list_editable = ["is_active"]


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ["name", "base_cost", "free_shipping_min", "estimated_days", "is_active", "order"]
    list_editable = ["is_active", "order", "base_cost"]
    search_fields = ["name", "cities"]


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ["name", "rate", "is_active", "is_default"]
    list_editable = ["is_active", "is_default"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "action", "model_name", "object_repr"]
    list_filter = ["action", "created_at"]
    search_fields = ["user__username", "object_repr", "details"]
    readonly_fields = ["created_at", "user", "action", "model_name", "object_id", "object_repr", "details", "ip_address"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["method", "name", "phone_number", "is_active"]
    list_editable = ["phone_number", "is_active"]
    search_fields = ["method", "phone_number", "name"]
