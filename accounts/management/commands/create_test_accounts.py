"""
Management-Command zum Erstellen von Test-Accounts für E2E-Tests
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from subscriptions.models import SubscriptionPlan, UserSubscription
from django.db import transaction


class Command(BaseCommand):
    help = 'Erstellt Test-Accounts mit verschiedenen Benutzerrechten (Basic, Premium, Admin)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Erzwingt das Überschreiben bestehender Test-Accounts',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Stelle sicher, dass alle Subscription-Pläne existieren
        self.ensure_subscription_plans()
        
        # Test-Accounts definieren
        test_accounts = [
            {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'plan': 'basic',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'username': 'premiumuser',
                'email': 'premiumuser@example.com',
                'password': 'premiumpass123',
                'first_name': 'Premium',
                'last_name': 'User',
                'plan': 'premium',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'adminpass123',
                'first_name': 'Admin',
                'last_name': 'User',
                'plan': 'premium',  # Admin bekommt Premium-Rechte
                'is_staff': True,
                'is_superuser': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for account_data in test_accounts:
            username = account_data['username']
            plan_name = account_data['plan']
            
            try:
                with transaction.atomic():
                    # Prüfe ob User bereits existiert
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': account_data['email'],
                            'first_name': account_data['first_name'],
                            'last_name': account_data['last_name'],
                            'is_staff': account_data['is_staff'],
                            'is_superuser': account_data['is_superuser']
                        }
                    )
                    
                    if created:
                        # Setze Passwort für neuen User
                        user.set_password(account_data['password'])
                        user.save()
                        
                        # Erstelle UserProfile (überschreibt falls vorhanden)
                        UserProfile.objects.filter(user=user).delete()
                        UserProfile.objects.create(user=user)
                        
                        # Erstelle Subscription
                        plan = SubscriptionPlan.objects.get(name=plan_name)
                        subscription = UserSubscription.objects.create(
                            user=user,
                            plan=plan
                        )
                        
                        # Für Premium-User: Starte Trial
                        if plan_name == 'premium':
                            subscription.start_premium_trial()
                        
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Test-Account "{username}" ({plan_name}) erstellt')
                        )
                        
                    elif force:
                        # Update bestehenden User
                        user.email = account_data['email']
                        user.first_name = account_data['first_name']
                        user.last_name = account_data['last_name']
                        user.is_staff = account_data['is_staff']
                        user.is_superuser = account_data['is_superuser']
                        user.set_password(account_data['password'])
                        user.save()
                        
                        # Update oder erstelle UserProfile
                        profile, profile_created = UserProfile.objects.get_or_create(user=user)
                        
                        # Update oder erstelle Subscription
                        plan = SubscriptionPlan.objects.get(name=plan_name)
                        subscription, sub_created = UserSubscription.objects.get_or_create(
                            user=user,
                            defaults={'plan': plan}
                        )
                        
                        if not sub_created:
                            subscription.plan = plan
                            subscription.save()
                        
                        # Für Premium-User: Starte Trial
                        if plan_name == 'premium':
                            subscription.start_premium_trial()
                        
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Test-Account "{username}" ({plan_name}) aktualisiert')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Test-Account "{username}" existiert bereits (--force zum Überschreiben)')
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Fehler beim Erstellen von "{username}": {str(e)}')
                )
        
        # Zusammenfassung
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 ZUSAMMENFASSUNG:')
        self.stdout.write(f'✅ {created_count} neue Test-Accounts erstellt')
        self.stdout.write(f'🔄 {updated_count} Test-Accounts aktualisiert')
        self.stdout.write('\n🔑 ANMELDEDATEN:')
        self.stdout.write('Basic-User: testuser / testpass123')
        self.stdout.write('Premium-User: premiumuser / premiumpass123')
        self.stdout.write('Admin-User: admin / adminpass123')
        self.stdout.write('\n💡 Verwendung:')
        self.stdout.write('python manage.py create_test_accounts --force  # Überschreibt bestehende Accounts')
        self.stdout.write('='*50)
        
    def ensure_subscription_plans(self):
        """Stellt sicher, dass alle Subscription-Pläne existieren"""
        try:
            # Führe das set_premium Command aus
            from django.core.management import call_command
            call_command('set_premium', verbosity=0)
            self.stdout.write('✅ Subscription-Pläne sichergestellt')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Fehler beim Erstellen der Subscription-Pläne: {str(e)}')
            ) 