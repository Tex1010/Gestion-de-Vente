from django.contrib import admin

from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Identite visuelle",
            {
                "fields": (
                    "site_name",
                    "site_tagline",
                    "logo",
                )
            },
        ),
        (
            "Accueil",
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                )
            },
        ),
        (
            "Page a propos et contact",
            {
                "fields": (
                    "about_title",
                    "about_content",
                    "contact_phone",
                    "address",
                    "whatsapp_url",
                    "facebook_url",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()
