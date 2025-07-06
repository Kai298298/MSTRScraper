from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    """
    Django-Management-Command zum automatischen Erstellen eines Test-Users.
    
    Verwendung:
    python manage.py create_test_user
    
    Erstellt einen normalen User mit folgenden Credentials:
    - Username: testuser
    - Email: test@mstrscraper.de
    - Password: testpass123
    """
    
    help = 'Erstellt automatisch einen Test-User für das System'

    def handle(self, *args, **options):
        username = 'testuser'
        email = 'test@mstrscraper.de'
        password = 'testpass123'
        
        try:
            # Prüfen ob User bereits existiert
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                # Passwort aktualisieren falls nötig
                if not user.check_password(password):
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        f'✅ Test-User "{username}" existiert bereits - Passwort wurde aktualisiert'
                    )
                else:
                    self.stdout.write(
                        f'✅ Test-User "{username}" existiert bereits mit korrektem Passwort'
                    )
            else:
                # Neuen User erstellen
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    f'✅ Test-User "{username}" erfolgreich erstellt!'
                )
            
            # Zusätzliche Informationen ausgeben
            self.stdout.write(
                f'\n📋 Test-User Details:\n'
                f'   Username: {username}\n'
                f'   Email: {email}\n'
                f'   Password: {password}\n'
                f'   Superuser: Nein\n'
                f'   Aktiv: {user.is_active}\n'
            )
            
        except IntegrityError as e:
            self.stdout.write(
                f'❌ Fehler beim Erstellen des Test-Users: {e}'
            )
        except Exception as e:
            self.stdout.write(
                f'❌ Unerwarteter Fehler: {e}'
            ) 