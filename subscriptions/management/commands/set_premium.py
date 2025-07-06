from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Erstellt die Standard-Abonnement-Pläne mit aktualisierten Preisen und Testversion'

    def handle(self, *args, **options):
        # Lösche bestehende Pläne
        SubscriptionPlan.objects.all().delete()
        
        # Erstelle neue Pläne
        plans_data = [
            {
                'name': 'free',
                'display_name': 'Kostenlos',
                'description': 'Perfekt zum Einstieg und Testen der Grundfunktionen',
                'price': 0.00,
                'requests_per_day': 10,
                'max_filters': 3,
                'can_export': False,
                'can_share': False,
            },
            {
                'name': 'basic',
                'display_name': 'Basic',
                'description': 'Ideal für kleine Unternehmen und Einzelunternehmer',
                'price': 49.00,
                'requests_per_day': 100,
                'max_filters': 5,
                'can_export': True,
                'can_share': False,
            },
            {
                'name': 'premium',
                'display_name': 'Premium',
                'description': 'Professionelle Lösung mit allen Features und 14 Tage kostenlos testen',
                'price': 99.00,
                'requests_per_day': 999999,  # Unbegrenzt
                'max_filters': 999999,  # Alle Filter
                'can_export': True,
                'can_share': True,
            },
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Plan "{plan.display_name}" erstellt')
                )
            else:
                # Update bestehenden Plan
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Plan "{plan.display_name}" aktualisiert')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Alle Abonnement-Pläne wurden erfolgreich erstellt/aktualisiert!')
        )
