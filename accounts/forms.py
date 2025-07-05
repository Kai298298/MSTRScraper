from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from subscriptions.models import UserSubscription


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


class UserSubscriptionForm(forms.ModelForm):
    """Formular für die Bearbeitung der Benutzerabonnements"""

    class Meta:
        model = UserSubscription
        fields = ["plan"]
        widgets = {"plan": forms.Select(attrs={"class": "form-control"})}
