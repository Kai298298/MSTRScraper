"""
Management-Command zum Vergeben von Premium-Rechten an einen User
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionPlan, UserSubscription
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Gibt einem User Premium-Rechte für eine bestimmte Zeit'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Benutzername des Users'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Anzahl der Tage für Premium (Standard: 30)'
        )
        parser.add_argument(
            '--plan',
            type=str,
            default='premium',
            choices=['basic', 'premium'],
            help='Premium-Plan (Standard: premium)'
        )

    def handle(self, *args, **options):
        username = options['username']
        days = options['days']
        plan_name = options['plan']

        self.stdout.write(
            self.style.SUCCESS(f'🎯 Vergebe {plan_name.upper()}-Rechte an {username}...')
        )

        try:
            # User finden
            user = User.objects.get(username=username)
            self.stdout.write(f"✅ User '{username}' gefunden")
        except User.DoesNotExist:
            raise CommandError(f"❌ User '{username}' nicht gefunden")

        try:
            # Premium-Plan finden
            plan = SubscriptionPlan.objects.get(name=plan_name)
            self.stdout.write(f"✅ Plan '{plan.display_name}' gefunden")
        except SubscriptionPlan.DoesNotExist:
            raise CommandError(f"❌ Plan '{plan_name}' nicht gefunden")

        # Bestehende Subscription löschen falls vorhanden
        UserSubscription.objects.filter(user=user).delete()

        # Neue Premium-Subscription erstellen
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)

        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            is_trial=False  # Kein Trial, sondern echte Premium-Zeit
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 {plan.display_name}-Rechte erfolgreich vergeben!'
            )
        )
        self.stdout.write(f"📅 Gültig von: {start_date.strftime('%d.%m.%Y')}")
        self.stdout.write(f"📅 Gültig bis: {end_date.strftime('%d.%m.%Y')}")
        self.stdout.write(f"📊 Anfragen pro Tag: {plan.requests_per_day}")
        self.stdout.write(f"🔍 Max. Filter: {plan.max_filters}")
        self.stdout.write(f"📤 Export möglich: {'Ja' if plan.can_export else 'Nein'}")
        self.stdout.write(f"🔗 Teilen möglich: {'Ja' if plan.can_share else 'Nein'}")

        # User-Status anzeigen
        self.stdout.write(
            self.style.WARNING(
                f'\n👤 User-Status für {username}:'
            )
        )
        self.stdout.write(f"   - Premium aktiv: {subscription.is_active}")
        self.stdout.write(f"   - Plan: {subscription.plan.display_name}")
        self.stdout.write(f"   - Verbleibende Tage: {(end_date - datetime.now()).days}")

        self.stdout.write(
            self.style.SUCCESS('\n✅ Premium-Rechte erfolgreich vergeben!')
        ) 