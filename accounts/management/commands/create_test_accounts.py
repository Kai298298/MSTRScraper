"""
Management-Command zum Erstellen von Test-Accounts für E2E-Tests
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from subscriptions.models import SubscriptionPlan, UserSubscription
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Erstellt Test-Accounts für E2E-Tests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Erzwingt das Überschreiben bestehender Test-Accounts',
        )

    def handle(self, *args, **options):
        self.stdout.write("🧪 Erstelle Test-Accounts für E2E-Tests...")
        
        # Test-Accounts definieren
        test_accounts = [
            {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
                'subscription_type': 'premium'
            },
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'adminpass123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'subscription_type': 'premium'
            },
            {
                'username': 'basicuser',
                'email': 'basicuser@example.com',
                'password': 'basicpass123',
                'first_name': 'Basic',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
                'subscription_type': 'basic'
            }
        ]
        
        # Premium-Plan erstellen falls nicht vorhanden
        premium_plan, created = SubscriptionPlan.objects.get_or_create(
            name='premium',
            defaults={
                'display_name': 'Premium',
                'description': 'Unbegrenzte Anfragen, Export, Analytics',
                'price': 99.99,
                'requests_per_day': 1000,
                'max_filters': 50,
                'can_export': True,
                'can_share': True
            }
        )
        
        basic_plan, created = SubscriptionPlan.objects.get_or_create(
            name='basic',
            defaults={
                'display_name': 'Basic',
                'description': 'Erweiterte Funktionen',
                'price': 49.99,
                'requests_per_day': 100,
                'max_filters': 10,
                'can_export': True,
                'can_share': False
            }
        )
        
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            name='free',
            defaults={
                'display_name': 'Kostenlos',
                'description': 'Basis-Funktionen',
                'price': 0.00,
                'requests_per_day': 10,
                'max_filters': 3,
                'can_export': False,
                'can_share': False
            }
        )
        
        created_count = 0
        updated_count = 0
        
        for account_data in test_accounts:
            username = account_data['username']
            
            # Prüfe ob User bereits existiert
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': account_data['email'],
                    'first_name': account_data['first_name'],
                    'last_name': account_data['last_name'],
                    'is_staff': account_data['is_staff'],
                    'is_superuser': account_data['is_superuser'],
                    'is_active': True
                }
            )
            
            if created:
                # Passwort setzen
                user.set_password(account_data['password'])
                user.save()
                
                # UserProfile erstellen
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'company_name': f"{account_data['first_name']} {account_data['last_name']} GmbH",
                        'city': 'Berlin',
                        'phone': '+49 30 12345678'
                    }
                )
                
                # Subscription erstellen
                if account_data['subscription_type'] == 'premium':
                    plan = premium_plan
                else:
                    plan = basic_plan
                    
                subscription, sub_created = UserSubscription.objects.get_or_create(
                    user=user,
                    defaults={
                        'plan': plan,
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=365),
                        'is_active': True
                    }
                )
                
                created_count += 1
                self.stdout.write(f"✅ Test-Account erstellt: {username}")
                
            elif options['force']:
                # User existiert bereits, aber --force wurde verwendet
                user.email = account_data['email']
                user.first_name = account_data['first_name']
                user.last_name = account_data['last_name']
                user.is_staff = account_data['is_staff']
                user.is_superuser = account_data['is_superuser']
                user.set_password(account_data['password'])
                user.save()
                
                updated_count += 1
                self.stdout.write(f"🔄 Test-Account aktualisiert: {username}")
            else:
                self.stdout.write(f"⚠️ Test-Account existiert bereits: {username}")
        
        self.stdout.write(f"\n📊 Zusammenfassung:")
        self.stdout.write(f"   ✅ Erstellt: {created_count}")
        self.stdout.write(f"   🔄 Aktualisiert: {updated_count}")
        self.stdout.write(f"   📋 Gesamt: {created_count + updated_count}")
        
        self.stdout.write(f"\n🔑 Test-Accounts:")
        self.stdout.write(f"   👤 testuser / testpass123 (Premium)")
        self.stdout.write(f"   👑 admin / adminpass123 (Admin)")
        self.stdout.write(f"   👤 basicuser / basicpass123 (Basic)")
        
        self.stdout.write(f"\n💡 Verwendung:")
        self.stdout.write(f"   python manage.py create_test_accounts --force")
        self.stdout.write(f"   python tests/e2e_test_app.py")
        
        self.stdout.write(self.style.SUCCESS("✅ Test-Accounts erfolgreich erstellt!")) 