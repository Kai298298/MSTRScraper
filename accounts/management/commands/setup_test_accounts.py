from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    """
    Django-Management-Command zum automatischen Erstellen aller Test-Accounts.
    
    Verwendung:
    python manage.py setup_test_accounts
    
    Erstellt folgende Accounts:
    1. Admin-Account:
       - Username: admin
       - Email: admin@mstrscraper.de
       - Password: admin123
       - Superuser: Ja
    
    2. Test-User-Account:
       - Username: testuser
       - Email: test@mstrscraper.de
       - Password: testpass123
       - Superuser: Nein
    """
    
    help = 'Erstellt automatisch alle Test-Accounts für das System'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starte Setup der Test-Accounts...\n')
        
        # Admin-Account erstellen
        self.create_admin_user()
        
        # Test-User erstellen
        self.create_test_user()
        
        self.stdout.write('\n✅ Setup der Test-Accounts abgeschlossen!')
        self.stdout.write('\n📋 Verfügbare Test-Accounts:')
        self.stdout.write('   🔑 Admin: admin / admin123')
        self.stdout.write('   👤 Test: testuser / testpass123')

    def create_admin_user(self):
        """Admin-Account erstellen oder aktualisieren"""
        username = 'admin'
        email = 'admin@mstrscraper.de'
        password = 'admin123'
        
        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    user.set_password(password)
                    user.save()
                    self.stdout.write(f'✅ Admin-Account "{username}" - Passwort aktualisiert')
                else:
                    self.stdout.write(f'✅ Admin-Account "{username}" - Bereits vorhanden')
            else:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(f'✅ Admin-Account "{username}" - Erstellt')
        except Exception as e:
            self.stdout.write(f'❌ Fehler beim Admin-Account: {e}')

    def create_test_user(self):
        """Test-User erstellen oder aktualisieren"""
        username = 'testuser'
        email = 'test@mstrscraper.de'
        password = 'testpass123'
        
        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    user.set_password(password)
                    user.save()
                    self.stdout.write(f'✅ Test-User "{username}" - Passwort aktualisiert')
                else:
                    self.stdout.write(f'✅ Test-User "{username}" - Bereits vorhanden')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(f'✅ Test-User "{username}" - Erstellt')
        except Exception as e:
            self.stdout.write(f'❌ Fehler beim Test-User: {e}') 