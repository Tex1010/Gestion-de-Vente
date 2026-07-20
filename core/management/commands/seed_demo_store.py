from django.core.management.base import BaseCommand

from catalog.models import Category, Product
from core.models import SiteConfiguration


class Command(BaseCommand):
    help = "Charge un jeu de donnees de demonstration pour la boutique."

    def handle(self, *args, **options):
        config = SiteConfiguration.load()
        config.site_name = "CVB Store"
        config.site_tagline = "Boutique en ligne moderne pour vos ventes quotidiennes."
        config.hero_title = "Bienvenue dans votre boutique digitale"
        config.hero_subtitle = (
            "Exposez vos produits par categorie, recevez des commandes propres et "
            "pilotez votre vitrine depuis l'administration."
        )
        config.about_title = "Une boutique simple a administrer"
        config.about_content = (
            "Cette plateforme a ete pensee pour permettre une gestion fluide des "
            "produits, du branding du site et du suivi des commandes."
        )
        config.contact_phone = "+261 34 00 000 00"
        config.address = "Antananarivo, Madagascar"
        config.whatsapp_url = "https://wa.me/261340000000"
        config.facebook_url = "https://facebook.com"
        config.save()

        produits_demo = {
            "Electronique": [
                ("Smartphone Nova X", "Telephone rapide, elegant et fiable.", 1200000, 18, True),
                ("Casque Pulse Air", "Son clair pour travail et loisirs.", 180000, 24, False),
            ],
            "Mode": [
                ("Chemise Premium", "Coupe moderne pour un style pro.", 85000, 30, True),
                ("Sac Urban Pro", "Sac pratique pour usage quotidien.", 145000, 12, False),
            ],
            "Maison": [
                ("Lampe Aura", "Design contemporain pour salon ou bureau.", 95000, 16, False),
                ("Chaise Loft", "Confort et finition moderne.", 220000, 8, True),
            ],
        }

        for category_name, products in produits_demo.items():
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    "description": f"Collection {category_name.lower()} disponible dans la boutique.",
                },
            )
            for name, short_description, price, stock, featured in products:
                Product.objects.get_or_create(
                    category=category,
                    name=name,
                    defaults={
                        "short_description": short_description,
                        "description": short_description,
                        "price": price,
                        "stock": stock,
                        "is_featured": featured,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Donnees de demonstration chargees avec succes."))
