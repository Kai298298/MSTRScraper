from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscriptions.models import UserSubscription, SubscriptionPlan


class Command(BaseCommand):
    help = 'Setzt einen Benutzer auf Premium-Tarif'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Benutzername')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            premium_plan = SubscriptionPlan.objects.get(name='premium')

            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                defaults={'plan': premium_plan}
            )

            if not created:
                subscription.plan = premium_plan
                subscription.save()

            self.stdout.write(
                self.style.SUCCESS(f'Benutzer {username} erfolgreich auf Premium-Tarif gesetzt!')
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Benutzer {username} nicht gefunden!')
            )
        except SubscriptionPlan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Premium-Tarif nicht gefunden!')
            )
