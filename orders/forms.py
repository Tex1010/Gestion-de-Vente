from django import forms

from core.models import PaymentMethod, ShippingZone
from orders.models import Order


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=150)
    phone = forms.CharField(label="Téléphone de contact", max_length=40)
    email = forms.EmailField(label="Email", required=False)
    city = forms.CharField(label="Ville", max_length=120, required=False)
    address = forms.CharField(label="Adresse", max_length=255, required=False)
    notes = forms.CharField(
        label="Notes (optionnel)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    # Mode de réception
    delivery_method = forms.ChoiceField(
        choices=[
            ("pickup", "Retrait sur place"),
            ("ship", "Livraison"),
        ],
        label="Mode de réception",
        required=True,
        widget=forms.RadioSelect(attrs={"class": "btn-check"}),
    )
    shipping_zone = forms.ChoiceField(
        choices=[],
        label="Zone de livraison",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    # Paiement
    payment_method = forms.ChoiceField(
        choices=[("", "Choisir un mode de paiement")],
        label="Mode de paiement",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    payment_phone = forms.CharField(
        label="Numéro marchand (destinataire)",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    )
    client_payment_phone = forms.CharField(
        label="Votre numéro de téléphone utilisé pour le paiement",
        required=True,
        max_length=40,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+261 34 00 000 00"}),
        help_text="Entrez le numéro de téléphone avec lequel vous avez effectué le paiement",
    )
    payment_reference = forms.CharField(
        label="Référence de paiement",
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: MV123ABC"}),
        help_text="Entrez la référence de votre transaction après le paiement",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Définir les choix du mode de réception
        self.fields["delivery_method"].choices = [
            ("pickup", "Retrait sur place"),
            ("ship", "Livraison"),
        ]

        # Charger dynamiquement les zones de livraison actives
        shipping_choices = [("", "Sélectionnez votre zone")]
        try:
            shipping_choices += [
                (str(z.pk), f"{z.name} — {z.base_cost:,.0f} Ar".replace(",", " "))
                for z in ShippingZone.objects.filter(is_active=True).order_by("order", "name")
            ]
        except Exception:
            pass
        self.fields["shipping_zone"].choices = shipping_choices

        # Charger dynamiquement les modes de paiement
        payment_choices = [("", "Choisir un mode de paiement")]
        try:
            payment_choices += [
                (pm.method, f"{pm.get_method_display()} - {pm.name or pm.phone_number}")
                for pm in PaymentMethod.objects.filter(is_active=True)
            ]
        except Exception:
            pass
        self.fields["payment_method"].choices = payment_choices

        # Appliquer les classes CSS
        for field_name, field in self.fields.items():
            if field_name == "payment_method":
                field.widget.attrs["class"] = "form-select"
            elif field_name == "payment_phone":
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["readonly"] = "readonly"
            else:
                css_class = field.widget.attrs.get("class", "")
                if "btn-check" not in css_class and "form-select" not in css_class:
                    field.widget.attrs["class"] = "form-control"