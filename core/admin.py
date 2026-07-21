from django.contrib import admin

from .models import ContactMessage, FAQ, PageContent, SiteConfiguration


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