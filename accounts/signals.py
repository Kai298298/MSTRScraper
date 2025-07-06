from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import connection
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal: Erstellt automatisch ein UserProfile für jeden neuen User.
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"UserProfile für User '{instance.username}' erstellt")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal: Speichert das UserProfile wenn der User gespeichert wird.
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Falls das Profil noch nicht existiert, erstelle es
        UserProfile.objects.create(user=instance)
        logger.info(f"UserProfile für User '{instance.username}' nachträglich erstellt")


def create_test_accounts_on_startup():
    """
    Funktion: Erstellt automatisch Test-Accounts beim ersten Start.
    Wird nur einmal ausgeführt, wenn keine Test-Accounts existieren.
    """
    try:
        # Prüfen ob bereits Test-Accounts existieren
        admin_exists = User.objects.filter(username='admin').exists()
        testuser_exists = User.objects.filter(username='testuser').exists()
        
        if not admin_exists or not testuser_exists:
            logger.info("🔧 Erstelle automatisch Test-Accounts...")
            
            # Admin-Account erstellen (falls nicht vorhanden)
            if not admin_exists:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@mstrscraper.de',
                    password='admin123'
                )
                logger.info("✅ Admin-Account 'admin' automatisch erstellt")
            
            # Test-User erstellen (falls nicht vorhanden)
            if not testuser_exists:
                test_user = User.objects.create_user(
                    username='testuser',
                    email='test@mstrscraper.de',
                    password='testpass123'
                )
                logger.info("✅ Test-User 'testuser' automatisch erstellt")
            
            logger.info("🎉 Test-Accounts Setup abgeschlossen!")
            logger.info("📋 Verfügbare Accounts:")
            logger.info("   🔑 Admin: admin / admin123")
            logger.info("   👤 Test: testuser / testpass123")
        else:
            logger.debug("✅ Test-Accounts bereits vorhanden")
            
    except Exception as e:
        logger.error(f"❌ Fehler beim automatischen Erstellen der Test-Accounts: {e}")


def check_and_create_test_accounts():
    """
    Prüft und erstellt Test-Accounts beim Django-Start.
    Wird nur ausgeführt, wenn die Datenbank bereit ist.
    """
    try:
        # Prüfen ob die Datenbank bereit ist
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test-Accounts erstellen
        create_test_accounts_on_startup()
        
    except Exception as e:
        logger.warning(f"⚠️ Datenbank noch nicht bereit für Test-Accounts: {e}")
        # Versuche es später nochmal
        pass 