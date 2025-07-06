from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta


class UserProfile(models.Model):
    """Erweitertes Benutzerprofil mit E-Mail-Verifikation"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)
    
    # Adressfelder für Rechnungszwecke
    company_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Firmenname")
    street_address = models.CharField(max_length=200, blank=True, null=True, verbose_name="Straße & Hausnummer")
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Postleitzahl")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stadt")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Land")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefonnummer")
    tax_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Steuernummer/USt-IdNr.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil für {self.user.username}"

    def generate_verification_token(self):
        """Generiert einen neuen Verifikations-Token"""
        self.email_verification_token = get_random_string(64)
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_token

    def is_verification_token_valid(self):
        """Prüft ob der Verifikations-Token noch gültig ist (24 Stunden)"""
        if not self.email_verification_sent_at:
            return False
        expiry_time = self.email_verification_sent_at + timedelta(hours=24)
        return timezone.now() < expiry_time

    def verify_email(self, token):
        """Verifiziert die E-Mail-Adresse"""
        if (self.email_verification_token == token and 
            self.is_verification_token_valid()):
            self.email_verified = True
            self.email_verification_token = None
            self.email_verification_sent_at = None
            self.save()
            return True
        return False

    def send_verification_email(self):
        """Sendet eine neue Verifikations-E-Mail"""
        from django.core.mail import send_mail
        from django.conf import settings
        from django.urls import reverse
        
        token = self.generate_verification_token()
        verification_url = f"{settings.SITE_URL}{reverse('accounts:verify_email', args=[token])}"
        
        subject = "E-Mail-Adresse bestätigen - MaStR Lead Generator"
        message = f"""
Hallo {self.user.username},

vielen Dank für Ihre Registrierung beim MaStR Lead Generator!

Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Link klicken:

{verification_url}

Dieser Link ist 24 Stunden gültig.

Falls Sie sich nicht registriert haben, können Sie diese E-Mail ignorieren.

Mit freundlichen Grüßen
Ihr MaStR Lead Generator Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Fehler beim Senden der Verifikations-E-Mail: {e}")
            return False
