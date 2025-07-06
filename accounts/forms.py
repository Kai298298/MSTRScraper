from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from subscriptions.models import UserSubscription
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Erweitertes Registrierungsformular mit Datenschutz-Checkbox"""

    email = forms.EmailField(required=True, help_text="Erforderlich. Geben Sie eine gültige E-Mail-Adresse ein.")
    datenschutz_akzeptiert = forms.BooleanField(
        required=True,
        label="Ich akzeptiere die Datenschutzerklärung",
        help_text="Sie müssen der Datenschutzerklärung zustimmen, um sich zu registrieren.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "datenschutz_akzeptiert")

    def clean_datenschutz_akzeptiert(self):
        datenschutz = self.cleaned_data.get("datenschutz_akzeptiert")
        if not datenschutz:
            raise forms.ValidationError("Sie müssen der Datenschutzerklärung zustimmen.")
        return datenschutz


class CustomAuthenticationForm(AuthenticationForm):
    """Angepasstes Login-Formular"""

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Benutzername"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Passwort"}))


class UserProfileForm(forms.ModelForm):
    """Formular für die Bearbeitung des Benutzerprofils"""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class UserProfileAddressForm(forms.ModelForm):
    """Formular für die Adressfelder des Benutzerprofils"""

    class Meta:
        model = UserProfile
        fields = [
            'company_name', 'street_address', 'postal_code', 
            'city', 'country', 'phone', 'tax_id'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Firmenname (optional)'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Straße & Hausnummer'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postleitzahl'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stadt'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Land', 'value': 'Deutschland'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefonnummer'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Steuernummer oder USt-IdNr.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Setze Deutschland als Standard-Land
        if not self.instance.pk or not self.instance.country:
            self.fields['country'].initial = 'Deutschland'


class UserSubscriptionForm(forms.ModelForm):
    """Formular für die Bearbeitung der Benutzerabonnements"""

    class Meta:
        model = UserSubscription
        fields = ["plan"]
        widgets = {"plan": forms.Select(attrs={"class": "form-control"})}
