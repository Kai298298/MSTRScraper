from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Erstellt UserProfile für bestehende Benutzer, die noch keines haben'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        
        if users_without_profile.exists():
            self.stdout.write(f"Erstelle UserProfile für {users_without_profile.count()} Benutzer...")
            
            for user in users_without_profile:
                UserProfile.objects.create(user=user)
                self.stdout.write(f"UserProfile erstellt für: {user.username}")
            
            self.stdout.write(
                self.style.SUCCESS(f"Erfolgreich {users_without_profile.count()} UserProfile(s) erstellt!")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Alle Benutzer haben bereits ein UserProfile!")
            ) 