"""
Django Management Command für E2E-Tests mit Playwright
"""

import asyncio
import sys
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

# Playwright-Import hinzufügen
sys.path.append(os.path.join(settings.BASE_DIR, 'tests'))
from e2e_test_app import E2ETestApp

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Führt umfassende E2E-Tests mit Playwright für die online-deployte App durch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://app.kairitter.de',
            help='URL der zu testenden Anwendung (Standard: https://app.kairitter.de)'
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Browser im Headless-Modus ausführen (ohne GUI)'
        )
        parser.add_argument(
            '--fast',
            action='store_true',
            help='Schnelle Tests ohne Verzögerungen'
        )
        parser.add_argument(
            '--screenshot',
            action='store_true',
            help='Screenshots bei Fehlern erstellen'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starte E2E-Tests mit Playwright...')
        )
        
        try:
            # E2E-Tests ausführen
            asyncio.run(self.run_e2e_tests(options))
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Tests wurden abgebrochen')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Fehler beim Ausführen der Tests: {str(e)}')
            )
            raise CommandError(f'E2E-Tests fehlgeschlagen: {str(e)}')

    async def run_e2e_tests(self, options):
        """Führt die E2E-Tests aus"""
        
        # Tester konfigurieren
        tester = E2ETestApp(options['url'])
        
        # Playwright-Optionen anpassen
        if options['headless']:
            # Headless-Modus für CI/CD
            tester.headless = True
            tester.slow_mo = 0
        elif options['fast']:
            # Schnelle Tests
            tester.slow_mo = 100
        else:
            # Normale Tests mit Verzögerung
            tester.slow_mo = 1000
            
        if options['screenshot']:
            tester.screenshot_on_error = True
            
        # Tests ausführen
        await tester.run_tests()
        
        # Ergebnisse ausgeben
        self.print_summary(tester)

    def print_summary(self, tester):
        """Gibt eine Zusammenfassung der Testergebnisse aus"""
        
        success_rate = (tester.success_count / tester.test_count * 100) if tester.test_count > 0 else 0
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🧪 E2E-TEST ZUSAMMENFASSUNG'))
        self.stdout.write('='*60)
        
        self.stdout.write(f"📊 Tests ausgeführt: {tester.test_count}")
        self.stdout.write(f"✅ Erfolgreich: {tester.success_count}")
        self.stdout.write(f"❌ Fehler: {len(tester.errors)}")
        self.stdout.write(f"⚠️ Warnungen: {len(tester.warnings)}")
        
        if success_rate >= 90:
            self.stdout.write(
                self.style.SUCCESS(f"📈 Erfolgsrate: {success_rate:.1f}% - EXCELLENT! 🎉")
            )
        elif success_rate >= 80:
            self.stdout.write(
                self.style.WARNING(f"📈 Erfolgsrate: {success_rate:.1f}% - GUT")
            )
        elif success_rate >= 70:
            self.stdout.write(
                self.style.WARNING(f"📈 Erfolgsrate: {success_rate:.1f}% - BEFRIEDIGEND")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"📈 Erfolgsrate: {success_rate:.1f}% - KRITISCH!")
            )
            
        if tester.errors:
            self.stdout.write('\n❌ KRITISCHE FEHLER:')
            for error in tester.errors:
                self.stdout.write(
                    self.style.ERROR(f"  • {error}")
                )
                
        if tester.warnings:
            self.stdout.write('\n⚠️ WARNUNGEN:')
            for warning in tester.warnings:
                self.stdout.write(
                    self.style.WARNING(f"  • {warning}")
                )
                
        self.stdout.write('\n' + '='*60)
        
        # Empfehlungen basierend auf Ergebnissen
        if len(tester.errors) > 0:
            self.stdout.write(
                self.style.ERROR('🔧 EMPFEHLUNGEN:')
            )
            self.stdout.write(
                self.style.ERROR('  • Kritische Fehler müssen behoben werden')
            )
            self.stdout.write(
                self.style.ERROR('  • Überprüfen Sie die Server-Logs')
            )
            
        if len(tester.warnings) > 5:
            self.stdout.write(
                self.style.WARNING('🔧 EMPFEHLUNGEN:')
            )
            self.stdout.write(
                self.style.WARNING('  • Warnungen sollten überprüft werden')
            )
            self.stdout.write(
                self.style.WARNING('  • Performance-Optimierungen erwägen')
            )
            
        if success_rate >= 90 and len(tester.errors) == 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 EXCELLENT! Ihre App funktioniert perfekt!')
            ) 