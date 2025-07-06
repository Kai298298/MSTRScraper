from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)


class DataVisualizerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_visualizer'

    def ready(self):
        """
        Wird beim Django-Start ausgeführt.
        Koordiniert die automatische Erstellung von Test-Accounts.
        """
        # Verzögerte Ausführung nach der Migration
        post_migrate.connect(self._setup_test_accounts_after_migration, sender=self)
        
        logger.info("🚀 MSTRScraper Data Visualizer bereit")

    def _setup_test_accounts_after_migration(self, sender, **kwargs):
        """
        Erstellt Test-Accounts nach der Migration.
        Wird nur einmal ausgeführt.
        """
        try:
            from data_visualizer import setup_test_accounts_on_startup
            setup_test_accounts_on_startup()
        except Exception as e:
            logger.warning(f"⚠️ Fehler beim automatischen Setup der Test-Accounts: {e}") 