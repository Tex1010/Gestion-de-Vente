from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import UserProfile, Wishlist


class RegistrationForm(UserCreationForm):
    """Formulaire d'inscription avec email obligatoire."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "votre@email.com",
        }),
    )
    phone = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "+261 34 00 000 00",
        }),
        label="Téléphone",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Nom d'utilisateur",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "Mot de passe",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "Confirmer le mot de passe",
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Le profil est créé automatiquement via le signal
            profile = user.profile
            profile.phone = self.cleaned_data.get("phone", "")
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    """Formulaire de connexion personnalisé."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "Nom d'utilisateur ou email",
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "Mot de passe",
        })


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification du profil."""

    class Meta:
        model = UserProfile
        fields = ["phone", "address", "city", "avatar", "birth_date"]
        widgets = {
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+261 34 00 000 00",
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Votre adresse",
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Votre ville",
            }),
            "avatar": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "birth_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }


class UserInfoForm(forms.ModelForm):
    """Formulaire pour modifier les infos de base (nom, email)."""

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Cet email est déjà utilisé.")
        return email


class AddToWishlistForm(forms.Form):
    """Formulaire simple pour ajouter/retirer des favoris."""
    product_id = forms.IntegerField(widget=forms.HiddenInput())