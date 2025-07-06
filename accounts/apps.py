from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        Wird beim Django-Start ausgeführt.
        Importiert die Signals und erstellt Test-Accounts.
        """
        # Signals importieren
        import accounts.signals
        
        # Test-Accounts beim ersten Start erstellen
        from accounts.signals import check_and_create_test_accounts
        
        # Verzögerte Ausführung nach der Migration
        post_migrate.connect(self._create_test_accounts_after_migration, sender=self)
        
        logger.info("🚀 Accounts-App bereit - Test-Accounts werden automatisch erstellt")

    def _create_test_accounts_after_migration(self, sender, **kwargs):
        """
        Erstellt Test-Accounts nach der Migration.
        Wird nur einmal ausgeführt.
        """
        from accounts.signals import create_test_accounts_on_startup
        
        try:
            create_test_accounts_on_startup()
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim automatischen Erstellen der Test-Accounts: {e}")
