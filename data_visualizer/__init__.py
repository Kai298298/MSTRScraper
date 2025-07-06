"""
MSTRScraper - Data Visualizer
Hauptanwendung für die Visualisierung von MSTR-Daten
"""

import os
import logging
from django.apps import apps

logger = logging.getLogger(__name__)


def setup_test_accounts_on_startup():
    """
    Globale Funktion: Erstellt Test-Accounts beim Django-Start.
    Wird nur ausgeführt, wenn die Accounts-App bereit ist.
    """
    try:
        # Prüfen ob die Accounts-App bereit ist
        if apps.is_installed('accounts'):
            from accounts.signals import create_test_accounts_on_startup
            create_test_accounts_on_startup()
        else:
            logger.debug("Accounts-App noch nicht bereit")
    except Exception as e:
        logger.debug(f"Test-Accounts Setup noch nicht möglich: {e}")


# Django-Startup Hook
default_app_config = 'data_visualizer.apps.DataVisualizerConfig'
