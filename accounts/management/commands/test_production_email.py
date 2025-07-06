"""
Management-Command zum Testen der E-Mail-Konfiguration in der Produktion
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Testet die E-Mail-Konfiguration in der Produktion'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='E-Mail-Adresse für den Test'
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='Test E-Mail von MSTRScraper',
            help='Betreff der Test-E-Mail'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='Dies ist eine Test-E-Mail von MSTRScraper. Wenn Sie diese E-Mail erhalten, funktioniert die E-Mail-Konfiguration korrekt.',
            help='Nachricht der Test-E-Mail'
        )

    def handle(self, *args, **options):
        email = options['email']
        subject = options['subject']
        message = options['message']

        self.stdout.write(
            self.style.SUCCESS('🧪 Teste E-Mail-Konfiguration...')
        )

        # Zeige aktuelle E-Mail-Konfiguration
        self.stdout.write(f"📧 E-Mail-Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"📧 E-Mail-Host: {getattr(settings, 'EMAIL_HOST', 'Nicht gesetzt')}")
        self.stdout.write(f"📧 E-Mail-Port: {getattr(settings, 'EMAIL_PORT', 'Nicht gesetzt')}")
        self.stdout.write(f"📧 E-Mail-User: {getattr(settings, 'EMAIL_HOST_USER', 'Nicht gesetzt')}")
        self.stdout.write(f"📧 TLS aktiviert: {getattr(settings, 'EMAIL_USE_TLS', 'Nicht gesetzt')}")
        self.stdout.write(f"📧 From E-Mail: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Nicht gesetzt')}")

        # Prüfe ob SMTP konfiguriert ist
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Console-Backend aktiviert - E-Mails werden nur in der Konsole angezeigt'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '💡 Für echte E-Mails setzen Sie EMAIL_HOST_USER und EMAIL_HOST_PASSWORD in Coolify'
                )
            )

        try:
            # Sende Test-E-Mail
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                self.stdout.write(
                    self.style.SUCCESS(
                        '✅ Test-E-Mail wurde in der Konsole angezeigt (Console-Backend)'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        '📋 E-Mail-Inhalt wurde in den Logs ausgegeben'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Test-E-Mail wurde erfolgreich an {email} gesendet!'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Fehler beim Senden der E-Mail: {str(e)}')
            )
            
            # Detaillierte Fehleranalyse
            if 'authentication' in str(e).lower():
                self.stdout.write(
                    self.style.ERROR(
                        '🔐 Authentifizierungsfehler - Prüfen Sie EMAIL_HOST_USER und EMAIL_HOST_PASSWORD'
                    )
                )
            elif 'connection' in str(e).lower():
                self.stdout.write(
                    self.style.ERROR(
                        '🌐 Verbindungsfehler - Prüfen Sie EMAIL_HOST und EMAIL_PORT'
                    )
                )
            elif 'ssl' in str(e).lower() or 'tls' in str(e).lower():
                self.stdout.write(
                    self.style.ERROR(
                        '🔒 SSL/TLS-Fehler - Prüfen Sie EMAIL_USE_TLS und EMAIL_USE_SSL'
                    )
                )

            # Zeige Debug-Informationen
            self.stdout.write(
                self.style.WARNING(
                    '🔍 Debug-Informationen:'
                )
            )
            self.stdout.write(f"   - E-Mail-Backend: {settings.EMAIL_BACKEND}")
            self.stdout.write(f"   - E-Mail-Host: {getattr(settings, 'EMAIL_HOST', 'Nicht gesetzt')}")
            self.stdout.write(f"   - E-Mail-Port: {getattr(settings, 'EMAIL_PORT', 'Nicht gesetzt')}")
            self.stdout.write(f"   - E-Mail-User gesetzt: {'Ja' if getattr(settings, 'EMAIL_HOST_USER', None) else 'Nein'}")
            self.stdout.write(f"   - E-Mail-Password gesetzt: {'Ja' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Nein'}")

            raise CommandError(f'E-Mail-Test fehlgeschlagen: {str(e)}')

        self.stdout.write(
            self.style.SUCCESS('🎉 E-Mail-Test abgeschlossen!')
        ) 