from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscriptions.models import UserSubscription


class Command(BaseCommand):
    help = 'Startet eine Premium-Testversion für einen Benutzer'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Benutzername')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            
            # Prüfe, ob bereits eine Subscription existiert
            try:
                subscription = user.subscription
            except UserSubscription.DoesNotExist:
                # Erstelle neue Subscription mit Free-Plan
                from subscriptions.models import SubscriptionPlan
                free_plan = SubscriptionPlan.objects.get(name='free')
                subscription = UserSubscription.objects.create(
                    user=user,
                    plan=free_plan
                )

            # Starte Trial
            subscription.start_premium_trial()
            
            self.stdout.write(
                self.style.SUCCESS(f'Premium-Testversion für {username} gestartet!')
            )
            self.stdout.write(
                f'Trial endet am: {subscription.trial_end_date.strftime("%d.%m.%Y %H:%M")}'
            )
            self.stdout.write(
                f'Verbleibende Tage: {subscription.days_remaining_in_trial()}'
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Benutzer {username} nicht gefunden!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Fehler: {str(e)}')
            ) 