from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=150)
    phone = forms.CharField(label="Telephone", max_length=40)
    email = forms.EmailField(label="Email", required=False)
    city = forms.CharField(label="Ville", max_length=120)
    address = forms.CharField(label="Adresse", max_length=255)
    notes = forms.CharField(
        label="Notes",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
