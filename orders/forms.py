from django import forms

from core.models import PaymentMethod


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=150)
    phone = forms.CharField(label="Téléphone de contact", max_length=40)
    email = forms.EmailField(label="Email", required=False)
    city = forms.CharField(label="Ville", max_length=120)
    address = forms.CharField(label="Adresse", max_length=255)
    notes = forms.CharField(
        label="Notes (optionnel)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
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

        for field_name, field in self.fields.items():
            if field_name == "payment_method":
                field.widget.attrs["class"] = "form-select"
            elif field_name == "payment_phone":
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["readonly"] = "readonly"
            else:
                field.widget.attrs["class"] = "form-control"
