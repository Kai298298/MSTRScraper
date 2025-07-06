from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    """
    Django-Management-Command zum automatischen Erstellen eines Admin-Accounts.
    
    Verwendung:
    python manage.py create_admin_user
    
    Erstellt einen Superuser mit folgenden Credentials:
    - Username: admin
    - Email: admin@mstrscraper.de
    - Password: admin123
    """
    
    help = 'Erstellt automatisch einen Admin-Account für das System'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@mstrscraper.de'
        password = 'admin123'
        
        try:
            # Prüfen ob User bereits existiert
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                # Passwort aktualisieren falls nötig
                if not user.check_password(password):
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Admin-Account "{username}" existiert bereits - Passwort wurde aktualisiert'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Admin-Account "{username}" existiert bereits mit korrektem Passwort'
                        )
                    )
            else:
                # Neuen Superuser erstellen
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Admin-Account "{username}" erfolgreich erstellt!'
                    )
                )
            
            # Zusätzliche Informationen ausgeben
            self.stdout.write(
                self.style.WARNING(
                    f'\n📋 Admin-Account Details:\n'
                    f'   Username: {username}\n'
                    f'   Email: {email}\n'
                    f'   Password: {password}\n'
                    f'   Superuser: Ja\n'
                    f'   Aktiv: {user.is_active}\n'
                )
            )
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Fehler beim Erstellen des Admin-Accounts: {e}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Unerwarteter Fehler: {e}'
                )
            ) 