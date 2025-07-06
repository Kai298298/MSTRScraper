from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    """
    Django-Management-Command zum Testen der E-Mail-Funktionalität.
    
    Verwendung:
    python manage.py test_email test@example.com
    """
    
    help = 'Testet die E-Mail-Funktionalität'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='E-Mail-Adresse zum Testen')

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write(f'🧪 Teste E-Mail-Versand an: {test_email}')
        self.stdout.write(f'📧 E-Mail-Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'🏠 E-Mail-Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'👤 E-Mail-User: {settings.EMAIL_HOST_USER}')
        
        try:
            # Test-E-Mail senden
            subject = "Test-E-Mail - MaStR Lead Generator"
            message = f"""
Hallo,

dies ist eine Test-E-Mail vom MaStR Lead Generator.

E-Mail-Konfiguration:
- Backend: {settings.EMAIL_BACKEND}
- Host: {settings.EMAIL_HOST}
- Port: {settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- User: {settings.EMAIL_HOST_USER}

Falls Sie diese E-Mail erhalten, funktioniert die E-Mail-Konfiguration korrekt!

Mit freundlichen Grüßen
MaStR Lead Generator Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Test-E-Mail erfolgreich gesendet an {test_email}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Fehler beim E-Mail-Versand: {e}'
                )
            )
            
            # Hilfreiche Tipps
            self.stdout.write('\n💡 Mögliche Lösungen:')
            self.stdout.write('1. Für Gmail: App-Passwort verwenden')
            self.stdout.write('2. Für lokale Tests: EMAIL_BACKEND auf console setzen')
            self.stdout.write('3. Firewall/SMTP-Port prüfen')
            self.stdout.write('4. E-Mail-Credentials überprüfen') 