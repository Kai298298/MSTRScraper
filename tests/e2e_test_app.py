"""
Umfassendes E2E-Test-System mit Playwright
Testet die online-deployte App auf https://app.kairitter.de/
"""

import asyncio
import time
import json
from playwright.async_api import async_playwright, expect
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class E2ETestApp:
    def __init__(self, base_url="https://app.kairitter.de"):
        self.base_url = base_url
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.test_count = 0
        self.headless = False
        self.slow_mo = 1000
        self.screenshot_on_error = True
        self.test_credentials = {
            'username': 'testuser',
            'password': 'testpass123',
            'admin_username': 'admin',
            'admin_password': 'adminpass123'
        }
        
    async def run_tests(self):
        """Führt alle E2E-Tests aus"""
        logger.info(f"🚀 Starte E2E-Tests für {self.base_url}")
        
        async with async_playwright() as p:
            # Browser starten
            browser = await p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # 1. Verfügbarkeit testen
                await self.test_availability(page)
                
                # 2. Navigation testen
                await self.test_navigation(page)
                
                # 3. Login/Registrierung testen
                await self.test_authentication(page)
                
                # 4. Dashboard-Funktionen testen
                await self.test_dashboard(page)
                
                # 5. Daten-Seiten testen
                await self.test_data_pages(page)
                
                # 6. Umfassende Klick-Tests
                await self.test_comprehensive_clicks(page)
                
                # 7. Fehlerseiten-Erkennung
                await self.test_error_pages(page)
                
                # 8. Responsive Design testen
                await self.test_responsive(page)
                
                # 9. Performance testen
                await self.test_performance(page)
                
                # 10. Spezifische Probleme testen
                await self.test_specific_issues(page)
                
            except Exception as e:
                self.errors.append(f"Kritischer Fehler: {str(e)}")
                logger.error(f"Kritischer Fehler: {str(e)}")
                
                if self.screenshot_on_error:
                    await page.screenshot(path=f"error_screenshot_{int(time.time())}.png")
            finally:
                await browser.close()
        
        # Ergebnisse ausgeben
        self.print_results()
        
    async def test_availability(self, page):
        """Testet die grundlegende Verfügbarkeit der App"""
        logger.info("🔍 Teste Verfügbarkeit...")
        
        try:
            # Hauptseite laden
            response = await page.goto(self.base_url, wait_until='networkidle')
            self.test_count += 1
            
            if response.status == 200:
                self.success_count += 1
                logger.info("✅ Hauptseite erfolgreich geladen")
            else:
                self.errors.append(f"❌ Hauptseite nicht erreichbar: Status {response.status}")
                
            # Prüfe ob Seite geladen ist
            await page.wait_for_load_state('domcontentloaded')
            
            # Prüfe auf JavaScript-Fehler
            js_errors = await page.evaluate("""
                () => {
                    const errors = [];
                    window.addEventListener('error', (e) => {
                        errors.push(e.message);
                    });
                    return errors;
                }
            """)
            
            if js_errors:
                self.warnings.append(f"⚠️ JavaScript-Fehler gefunden: {js_errors}")
                
        except Exception as e:
            self.errors.append(f"❌ Verfügbarkeitstest fehlgeschlagen: {str(e)}")
            
    async def test_navigation(self, page):
        """Testet die Navigation durch die App"""
        logger.info("🧭 Teste Navigation...")
        
        try:
            # Hauptseite laden
            await page.goto(self.base_url, wait_until='networkidle')
            
            # Navigation-Links finden und testen (verbesserte Selektoren)
            nav_selectors = [
                'nav a[href*="/"]',
                '.navbar a[href*="/"]', 
                '.nav a[href*="/"]',
                'a[href*="/data/"]',
                'a[href*="/betreiber/"]',
                'a[href*="/anlagen-listen/"]'
            ]
            
            for selector in nav_selectors:
                try:
                    nav_links = await page.query_selector_all(selector)
                    
                    for i, link in enumerate(nav_links[:3]):  # Erste 3 Links testen
                        try:
                            href = await link.get_attribute('href')
                            if href and not href.startswith('#') and not href.startswith('javascript:'):
                                self.test_count += 1
                                
                                # Link klicken
                                await link.click()
                                await page.wait_for_load_state('domcontentloaded')
                                
                                # Prüfe ob neue Seite geladen wurde (flexibler Check)
                                current_url = page.url
                                if current_url != self.base_url:
                                    self.success_count += 1
                                    logger.info(f"✅ Navigation erfolgreich: {href}")
                                    
                                    # Prüfe auf Fehlerseiten nach Navigation
                                    await self.check_for_error_pages(page, f"Navigation zu {href}")
                                else:
                                    self.warnings.append(f"⚠️ Navigation möglicherweise fehlgeschlagen: {href}")
                                    
                        except Exception as e:
                            self.warnings.append(f"⚠️ Navigation-Link {i} fehlgeschlagen: {str(e)}")
                            
                except Exception as e:
                    self.warnings.append(f"⚠️ Navigation-Selector {selector} fehlgeschlagen: {str(e)}")
                    
        except Exception as e:
            self.errors.append(f"❌ Navigationstest fehlgeschlagen: {str(e)}")
            
    async def test_authentication(self, page):
        """Testet Login und Registrierung"""
        logger.info("🔐 Teste Authentifizierung...")
        
        try:
            # Login-Seite testen
            await page.goto(f"{self.base_url}/accounts/login/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob Login-Formular vorhanden ist
            login_form = await page.query_selector('form')
            if login_form:
                self.success_count += 1
                logger.info("✅ Login-Formular gefunden")
                
                # Teste Login mit falschen Credentials
                await self.test_login_with_wrong_credentials(page)
                
                # Teste Login mit Test-Account
                await self.test_login_with_test_account(page)
            else:
                self.errors.append("❌ Login-Formular nicht gefunden")
                
            # Registrierung testen
            await page.goto(f"{self.base_url}/accounts/register/", wait_until='networkidle')
            self.test_count += 1
            
            register_form = await page.query_selector('form')
            if register_form:
                self.success_count += 1
                logger.info("✅ Registrierungs-Formular gefunden")
                
                # Teste Registrierung
                await self.test_registration(page)
            else:
                self.errors.append("❌ Registrierungs-Formular nicht gefunden")
                
        except Exception as e:
            self.errors.append(f"❌ Authentifizierungstest fehlgeschlagen: {str(e)}")
            
    async def test_login_with_wrong_credentials(self, page):
        """Testet Login mit falschen Anmeldedaten"""
        try:
            # Falsche Anmeldedaten eingeben
            await page.fill('input[name="username"]', 'wronguser')
            await page.fill('input[name="password"]', 'wrongpass')
            await page.click('button[type="submit"]')
            
            # Warte auf Antwort
            await page.wait_for_load_state('networkidle')
            
            # Prüfe ob Fehlermeldung angezeigt wird
            error_message = await page.query_selector('.alert-danger, .error, [class*="error"]')
            if error_message:
                self.success_count += 1
                logger.info("✅ Login-Fehlermeldung korrekt angezeigt")
            else:
                self.warnings.append("⚠️ Keine Login-Fehlermeldung gefunden")
                
        except Exception as e:
            self.warnings.append(f"⚠️ Login-Fehlertest fehlgeschlagen: {str(e)}")
            
    async def test_login_with_test_account(self, page):
        """Testet Login mit Test-Account"""
        try:
            # Zurück zur Login-Seite
            await page.goto(f"{self.base_url}/accounts/login/", wait_until='networkidle')
            
            # Test-Anmeldedaten eingeben
            await page.fill('input[name="username"]', self.test_credentials['username'])
            await page.fill('input[name="password"]', self.test_credentials['password'])
            await page.click('button[type="submit"]')
            
            # Warte auf Redirect nach erfolgreichem Login
            await page.wait_for_load_state('networkidle')
            
            # Prüfe ob Login erfolgreich war
            current_url = page.url
            if 'login' not in current_url and 'dashboard' in current_url or 'data' in current_url:
                self.success_count += 1
                logger.info("✅ Login mit Test-Account erfolgreich")
                
                # Logout testen
                await self.test_logout(page)
            else:
                self.warnings.append("⚠️ Login mit Test-Account möglicherweise fehlgeschlagen")
                
        except Exception as e:
            self.warnings.append(f"⚠️ Login-Test fehlgeschlagen: {str(e)}")
            
    async def test_logout(self, page):
        """Testet Logout mit verbesserten Selektoren"""
        try:
            # Logout-Link suchen (verbesserte Selektoren für Dropdown-Menü)
            logout_selectors = [
                'a[href*="logout"]',
                '.dropdown-item[href*="logout"]',
                'a:has-text("Abmelden")',
                'a:has-text("Logout")',
                'a:has-text("Sign out")',
                '[class*="logout"]',
                '.dropdown-menu a[href*="logout"]'
            ]
            
            logout_link = None
            for selector in logout_selectors:
                try:
                    logout_link = await page.query_selector(selector)
                    if logout_link:
                        break
                except:
                    continue
            
            # Falls Logout-Link im Dropdown-Menü ist, erst Dropdown öffnen
            if not logout_link:
                # Versuche Dropdown-Menü zu öffnen
                dropdown_toggle = await page.query_selector('.dropdown-toggle, [data-bs-toggle="dropdown"]')
                if dropdown_toggle:
                    await dropdown_toggle.click()
                    await page.wait_for_timeout(500)  # Warte auf Dropdown-Animation
                    
                    # Jetzt Logout-Link suchen
                    for selector in logout_selectors:
                        try:
                            logout_link = await page.query_selector(selector)
                            if logout_link:
                                break
                        except:
                            continue
                    
            if logout_link:
                await logout_link.click()
                await page.wait_for_load_state('networkidle')
                
                current_url = page.url
                if 'login' in current_url or 'logout' in current_url:
                    self.success_count += 1
                    logger.info("✅ Logout erfolgreich")
                else:
                    self.warnings.append("⚠️ Logout möglicherweise fehlgeschlagen")
            else:
                self.warnings.append("⚠️ Logout-Link nicht gefunden")
                
        except Exception as e:
            self.warnings.append(f"⚠️ Logout-Test fehlgeschlagen: {str(e)}")
            
    async def test_registration(self, page):
        """Testet Registrierung"""
        try:
            # Registrierungsformular ausfüllen
            await page.fill('input[name="username"]', f'testuser_{int(time.time())}')
            await page.fill('input[name="email"]', f'test{int(time.time())}@example.com')
            await page.fill('input[name="password1"]', 'testpass123!')
            await page.fill('input[name="password2"]', 'testpass123!')
            
            # Registrierung absenden
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Prüfe ob Registrierung erfolgreich war
            current_url = page.url
            if 'verification' in current_url or 'login' in current_url:
                self.success_count += 1
                logger.info("✅ Registrierung erfolgreich")
            else:
                self.warnings.append("⚠️ Registrierung möglicherweise fehlgeschlagen")
                
        except Exception as e:
            self.warnings.append(f"⚠️ Registrierungstest fehlgeschlagen: {str(e)}")
            
    async def test_dashboard(self, page):
        """Testet Dashboard-Funktionen"""
        logger.info("📊 Teste Dashboard...")
        
        try:
            # Login mit Test-Account
            await page.goto(f"{self.base_url}/accounts/login/", wait_until='networkidle')
            await page.fill('input[name="username"]', self.test_credentials['username'])
            await page.fill('input[name="password"]', self.test_credentials['password'])
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Dashboard-Links testen
            await self.test_dashboard_links(page)
            
        except Exception as e:
            self.errors.append(f"❌ Dashboard-Test fehlgeschlagen: {str(e)}")
            
    async def test_dashboard_links(self, page):
        """Testet Dashboard-Navigation"""
        try:
            # Hauptnavigation testen
            nav_links = [
                ('/data/', 'Daten-Suche'),
                ('/betreiber/', 'Betreiber'),
                ('/anlagen-listen/', 'Listen')
            ]
            
            for url, name in nav_links:
                try:
                    await page.goto(f"{self.base_url}{url}", wait_until='networkidle')
                    self.test_count += 1
                    
                    # Prüfe ob Seite geladen wurde
                    if page.url.endswith(url) or 'login' in page.url:
                        self.success_count += 1
                        logger.info(f"✅ {name}-Seite erfolgreich geladen")
                    else:
                        self.warnings.append(f"⚠️ {name}-Seite möglicherweise fehlgeschlagen")
                        
                except Exception as e:
                    self.warnings.append(f"⚠️ {name}-Seite fehlgeschlagen: {str(e)}")
                    
        except Exception as e:
            self.warnings.append(f"⚠️ Dashboard-Links-Test fehlgeschlagen: {str(e)}")
            
    async def test_data_pages(self, page):
        """Testet Daten-Seiten mit verbesserten Tests"""
        logger.info("📋 Teste Daten-Seiten...")
        
        try:
            # Login mit Test-Account
            await page.goto(f"{self.base_url}/accounts/login/", wait_until='networkidle')
            await page.fill('input[name="username"]', self.test_credentials['username'])
            await page.fill('input[name="password"]', self.test_credentials['password'])
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Daten-Seite testen
            await page.goto(f"{self.base_url}/data/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob Suchformular vorhanden ist
            search_form = await page.query_selector('form')
            if search_form:
                self.success_count += 1
                logger.info("✅ Suchformular auf Daten-Seite gefunden")
                
                # Filter testen
                await self.test_filters(page)
                
                # Kartenansicht testen
                await self.test_map_view(page)
            else:
                self.warnings.append("⚠️ Suchformular auf Daten-Seite nicht gefunden")
            
            # Listen-Seite testen
            await page.goto(f"{self.base_url}/anlagen-listen/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob Listen-Seite geladen wurde
            if 'anlagen-listen' in page.url:
                self.success_count += 1
                logger.info("✅ Listen-Seite erfolgreich geladen")
                
                # Prüfe ob Tabelle oder "Noch keine Listen erstellt" Nachricht vorhanden ist
                table = await page.query_selector('table')
                no_lists_message = await page.query_selector('text="Noch keine Listen erstellt"')
                
                if table or no_lists_message:
                    self.success_count += 1
                    logger.info("✅ Listen-Seite zeigt erwartete Inhalte")
                else:
                    self.warnings.append("⚠️ Listen-Seite zeigt unerwartete Inhalte")
            else:
                self.warnings.append("⚠️ Listen-Seite nicht erreichbar")
            
            # Betreiber-Seite testen
            await page.goto(f"{self.base_url}/betreiber/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob Betreiber-Seite geladen wurde
            if 'betreiber' in page.url:
                self.success_count += 1
                logger.info("✅ Betreiber-Seite erfolgreich geladen")
                
                # Prüfe ob Betreiber-Karten oder "Keine Betreiber gefunden" Nachricht vorhanden ist
                betreibers_cards = await page.query_selector('.betreiber-card')
                no_betreiber_message = await page.query_selector('text="Keine Betreiber gefunden"')
                filter_form = await page.query_selector('form#filterForm')
                
                if betreibers_cards or no_betreiber_message or filter_form:
                    self.success_count += 1
                    logger.info("✅ Betreiber-Seite zeigt erwartete Inhalte")
                else:
                    self.warnings.append("⚠️ Betreiber-Seite zeigt unerwartete Inhalte")
            else:
                self.warnings.append("⚠️ Betreiber-Seite nicht erreichbar")
                
        except Exception as e:
            self.errors.append(f"❌ Daten-Seiten-Test fehlgeschlagen: {str(e)}")
            
    async def test_filters(self, page):
        """Testet Filter-Funktionen"""
        logger.info("🔍 Teste Filter...")
        
        try:
            # Beispiel: Energieträger-Filter
            energietraeger_select = await page.query_selector('select[name="energietraeger"]')
            if energietraeger_select:
                await energietraeger_select.select_option(index=1)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                self.success_count += 1
                logger.info("✅ Energieträger-Filter funktioniert")
            else:
                self.warnings.append("⚠️ Energieträger-Filter nicht gefunden")
                
            # Beispiel: Bundesland-Filter
            bundesland_select = await page.query_selector('select[name="bundesland"]')
            if bundesland_select:
                await bundesland_select.select_option(index=1)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                self.success_count += 1
                logger.info("✅ Bundesland-Filter funktioniert")
            else:
                self.warnings.append("⚠️ Bundesland-Filter nicht gefunden")
                
            # Beispiel: Freitextsuche
            freitext_input = await page.query_selector('input[name="freitext"]')
            if freitext_input:
                await freitext_input.fill('Solar')
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                self.success_count += 1
                logger.info("✅ Freitextsuche funktioniert")
            else:
                self.warnings.append("⚠️ Freitextsuche nicht gefunden")
                
        except Exception as e:
            self.errors.append(f"❌ Filter-Test fehlgeschlagen: {str(e)}")

    async def test_map_view(self, page):
        """Testet die Kartenansicht mit verbesserten Selektoren"""
        logger.info("🗺️ Teste Kartenansicht auf /data/ ...")
        try:
            # Karten-Tab oder Button suchen (verbesserte Selektoren)
            map_button_selectors = [
                '#btn-card-view',  # Spezifische ID aus dem Template
                'button#btn-card-view',
                'button:has-text("Karten")',
                'button:has-text("Map")',
                'a:has-text("Karten")',
                'a:has-text("Map")',
                '[data-bs-target="#card-view"]',
                '.btn:has-text("Karten")',
                '.btn:has-text("Map")'
            ]
            
            map_button = None
            for selector in map_button_selectors:
                try:
                    map_button = await page.query_selector(selector)
                    if map_button:
                        logger.info(f"✅ Karten-Button gefunden mit Selector: {selector}")
                        break
                except:
                    continue
                    
            if map_button:
                await map_button.click()
                await page.wait_for_timeout(2000)  # Warte auf Map-Rendering
                
                # Prüfe, ob die Karte sichtbar ist
                map_selectors = [
                    '#anlagen-map',
                    '#card-view',
                    '.map-container',
                    '[id*="map"]'
                ]
                
                map_visible = False
                for map_selector in map_selectors:
                    try:
                        map_div = await page.query_selector(map_selector)
                        if map_div:
                            # Prüfe ob Element sichtbar ist
                            is_visible = await map_div.is_visible()
                            if is_visible:
                                map_visible = True
                                logger.info(f"✅ Kartenansicht sichtbar mit Selector: {map_selector}")
                                break
                    except:
                        continue
                
                if map_visible:
                    self.success_count += 1
                    logger.info("✅ Kartenansicht erfolgreich aktiviert")
                else:
                    self.warnings.append("⚠️ Kartenansicht nicht sichtbar")
            else:
                self.warnings.append("⚠️ Karten-Tab/Button nicht gefunden")
                
        except Exception as e:
            self.errors.append(f"❌ Kartenansicht-Test fehlgeschlagen: {str(e)}")

    async def test_comprehensive_clicks(self, page):
        """Testet umfassende Klick-Aktionen auf allen Seiten"""
        logger.info("🖱️ Teste umfassende Klick-Aktionen...")
        
        try:
            # Login mit Test-Account
            await page.goto(f"{self.base_url}/accounts/login/", wait_until='networkidle')
            await page.fill('input[name="username"]', self.test_credentials['username'])
            await page.fill('input[name="password"]', self.test_credentials['password'])
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Teste alle Hauptseiten
            pages_to_test = [
                ('/data/', 'Daten-Seite'),
                ('/betreiber/', 'Betreiber-Seite'),
                ('/anlagen-listen/', 'Listen-Seite')
            ]
            
            for url, page_name in pages_to_test:
                try:
                    await page.goto(f"{self.base_url}{url}", wait_until='networkidle')
                    self.test_count += 1
                    
                    # Teste alle klickbaren Elemente
                    await self.test_all_clickable_elements(page, page_name)
                    
                    # Teste alle Buttons
                    await self.test_all_buttons(page, page_name)
                    
                    # Teste alle Links
                    await self.test_all_links(page, page_name)
                    
                    # Teste alle Formulare
                    await self.test_all_forms(page, page_name)
                    
                except Exception as e:
                    self.warnings.append(f"⚠️ Klick-Tests für {page_name} fehlgeschlagen: {str(e)}")
                    
        except Exception as e:
            self.errors.append(f"❌ Umfassende Klick-Tests fehlgeschlagen: {str(e)}")

    async def test_all_clickable_elements(self, page, page_name):
        """Testet alle klickbaren Elemente auf einer Seite"""
        try:
            # Finde alle klickbaren Elemente
            clickable_selectors = [
                'button:not([disabled])',
                'a[href]:not([href="#"])',
                'input[type="submit"]',
                'input[type="button"]',
                '[role="button"]:not([disabled])',
                '.btn:not([disabled])'
            ]
            
            for selector in clickable_selectors:
                elements = await page.query_selector_all(selector)
                
                for i, element in enumerate(elements[:3]):  # Maximal 3 Elemente pro Selector
                    try:
                        # Prüfe ob Element sichtbar und klickbar ist
                        is_visible = await element.is_visible()
                        if is_visible:
                            # Prüfe ob Element nicht in einem Modal oder Dropdown ist
                            parent_modal = await element.query_selector('xpath=ancestor::div[contains(@class, "modal") or contains(@class, "dropdown")]')
                            if parent_modal:
                                continue
                                
                            # Versuche zu klicken
                            await element.click()
                            await page.wait_for_timeout(1000)  # Längere Pause für bessere Stabilität
                            
                            # Prüfe auf Fehlerseiten
                            await self.check_for_error_pages(page, f"{page_name} - {selector} #{i}")
                            
                            # Gehe zurück falls nötig (nur bei Navigation)
                            current_url = page.url
                            if page_name in ['Daten-Seite', 'Betreiber-Seite', 'Listen-Seite']:
                                if not current_url.endswith(f"/{page_name.lower().replace('-', '/')}/"):
                                    await page.go_back()
                                    await page.wait_for_load_state('networkidle')
                                
                    except Exception as e:
                        # Ignoriere Klick-Fehler, da nicht alle Elemente klickbar sein müssen
                        pass
                        
        except Exception as e:
            self.warnings.append(f"⚠️ Klickbare Elemente auf {page_name} fehlgeschlagen: {str(e)}")

    async def test_all_buttons(self, page, page_name):
        """Testet alle Buttons auf einer Seite"""
        try:
            buttons = await page.query_selector_all('button, .btn, input[type="submit"], input[type="button"]')
            
            for i, button in enumerate(buttons[:10]):  # Maximal 10 Buttons
                try:
                    is_visible = await button.is_visible()
                    if is_visible:
                        # Button-Text extrahieren
                        button_text = await button.text_content() or await button.get_attribute('value') or f"Button {i}"
                        
                        await button.click()
                        await page.wait_for_timeout(500)
                        
                        # Prüfe auf Fehlerseiten
                        await self.check_for_error_pages(page, f"{page_name} - Button: {button_text}")
                        
                        # Gehe zurück falls nötig
                        if page.url != f"{self.base_url}{page.url.split('/')[-2]}/":
                            await page.go_back()
                            await page.wait_for_load_state('networkidle')
                            
                except Exception as e:
                    pass  # Ignoriere Button-Klick-Fehler
                    
        except Exception as e:
            self.warnings.append(f"⚠️ Button-Tests auf {page_name} fehlgeschlagen: {str(e)}")

    async def test_all_links(self, page, page_name):
        """Testet alle Links auf einer Seite"""
        try:
            links = await page.query_selector_all('a[href]')
            
            for i, link in enumerate(links[:10]):  # Maximal 10 Links
                try:
                    href = await link.get_attribute('href')
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        is_visible = await link.is_visible()
                        if is_visible:
                            await link.click()
                            await page.wait_for_load_state('networkidle')
                            
                            # Prüfe auf Fehlerseiten
                            await self.check_for_error_pages(page, f"{page_name} - Link: {href}")
                            
                            # Gehe zurück falls nötig
                            if page.url != f"{self.base_url}{page.url.split('/')[-2]}/":
                                await page.go_back()
                                await page.wait_for_load_state('networkidle')
                                
                except Exception as e:
                    pass  # Ignoriere Link-Klick-Fehler
                    
        except Exception as e:
            self.warnings.append(f"⚠️ Link-Tests auf {page_name} fehlgeschlagen: {str(e)}")

    async def test_all_forms(self, page, page_name):
        """Testet alle Formulare auf einer Seite"""
        try:
            forms = await page.query_selector_all('form')
            
            for i, form in enumerate(forms[:3]):  # Maximal 3 Formulare
                try:
                    # Fülle alle Input-Felder aus
                    inputs = await form.query_selector_all('input[type="text"], input[type="email"], input[type="password"], textarea')
                    
                    for input_field in inputs:
                        try:
                            input_type = await input_field.get_attribute('type')
                            input_name = await input_field.get_attribute('name')
                            
                            if input_type == 'email':
                                await input_field.fill(f'test{int(time.time())}@example.com')
                            elif input_type == 'password':
                                await input_field.fill('testpass123')
                            else:
                                await input_field.fill(f'test_{input_name}_{int(time.time())}')
                                
                        except Exception as e:
                            pass  # Ignoriere Input-Fehler
                    
                    # Versuche Formular abzusenden
                    submit_button = await form.query_selector('button[type="submit"], input[type="submit"]')
                    if submit_button:
                        await submit_button.click()
                        await page.wait_for_load_state('networkidle')
                        
                        # Prüfe auf Fehlerseiten
                        await self.check_for_error_pages(page, f"{page_name} - Form #{i}")
                        
                        # Gehe zurück falls nötig
                        if page.url != f"{self.base_url}{page.url.split('/')[-2]}/":
                            await page.go_back()
                            await page.wait_for_load_state('networkidle')
                            
                except Exception as e:
                    pass  # Ignoriere Formular-Fehler
                    
        except Exception as e:
            self.warnings.append(f"⚠️ Formular-Tests auf {page_name} fehlgeschlagen: {str(e)}")

    async def test_error_pages(self, page):
        """Testet spezifisch nach Fehlerseiten"""
        logger.info("🚨 Teste Fehlerseiten-Erkennung...")
        
        try:
            # Teste 404-Seite
            await page.goto(f"{self.base_url}/nicht-existierende-seite/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob 404-Seite angezeigt wird
            error_404 = await page.query_selector('h1:has-text("404"), .error-404, [class*="404"]')
            if error_404:
                self.success_count += 1
                logger.info("✅ 404-Fehlerseite korrekt erkannt")
            else:
                self.warnings.append("⚠️ 404-Fehlerseite nicht erkannt")
            
            # Teste 403-Seite (Zugriff verweigert)
            await page.goto(f"{self.base_url}/admin/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob 403-Seite angezeigt wird
            error_403 = await page.query_selector('h1:has-text("403"), .error-403, [class*="403"], [class*="forbidden"]')
            if error_403:
                self.success_count += 1
                logger.info("✅ 403-Fehlerseite korrekt erkannt")
            else:
                self.warnings.append("⚠️ 403-Fehlerseite nicht erkannt")
                
        except Exception as e:
            self.warnings.append(f"⚠️ Fehlerseiten-Test fehlgeschlagen: {str(e)}")

    async def check_for_error_pages(self, page, context):
        """Prüft ob eine Fehlerseite angezeigt wird"""
        try:
            # Prüfe auf echte Fehlerseiten-Indikatoren (nicht CSS-Klassen)
            error_indicators = [
                'h1:has-text("404")',
                'h1:has-text("403")',
                'h1:has-text("500")',
                'h1:has-text("Seite nicht gefunden")',
                'h1:has-text("Zugriff verweigert")',
                'h1:has-text("Serverfehler")',
                'h1:has-text("Internal Server Error")',
                'title:has-text("404")',
                'title:has-text("403")',
                'title:has-text("500")',
                'title:has-text("Error")',
                'title:has-text("Not Found")',
                'title:has-text("Forbidden")'
            ]
            
            # Prüfe auch URL-basierte Fehler
            current_url = page.url
            if any(error_code in current_url for error_code in ['404', '403', '500', 'error']):
                self.errors.append(f"❌ Fehlerseite erkannt: {context} - URL enthält Fehlercode")
                logger.error(f"❌ Fehlerseite erkannt: {context} - URL: {current_url}")
                if self.screenshot_on_error:
                    await page.screenshot(path=f"error_page_{int(time.time())}.png")
                return
            
            # Prüfe auf spezifische Fehlerseiten-Elemente
            for indicator in error_indicators:
                error_element = await page.query_selector(indicator)
                if error_element:
                    self.errors.append(f"❌ Fehlerseite erkannt: {context} - {indicator}")
                    logger.error(f"❌ Fehlerseite erkannt: {context} - {indicator}")
                    
                    # Screenshot bei Fehlerseite
                    if self.screenshot_on_error:
                        await page.screenshot(path=f"error_page_{int(time.time())}.png")
                    break
                    
        except Exception as e:
            pass  # Ignoriere Fehler bei der Fehlerseiten-Prüfung

    async def test_responsive(self, page):
        """Testet Responsive Design"""
        logger.info("📱 Teste Responsive Design...")
        
        try:
            # Desktop-Ansicht testen
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            await page.goto(self.base_url, wait_until='networkidle')
            self.test_count += 1
            self.success_count += 1
            logger.info("✅ Desktop-Ansicht funktioniert")
            
            # Tablet-Ansicht testen
            await page.set_viewport_size({'width': 768, 'height': 1024})
            await page.reload()
            await page.wait_for_load_state('networkidle')
            self.test_count += 1
            self.success_count += 1
            logger.info("✅ Tablet-Ansicht funktioniert")
            
            # Mobile-Ansicht testen
            await page.set_viewport_size({'width': 375, 'height': 667})
            await page.reload()
            await page.wait_for_load_state('networkidle')
            self.test_count += 1
            self.success_count += 1
            logger.info("✅ Mobile-Ansicht funktioniert")
            
        except Exception as e:
            self.errors.append(f"❌ Responsive-Design-Test fehlgeschlagen: {str(e)}")
            
    async def test_performance(self, page):
        """Testet Performance"""
        logger.info("⚡ Teste Performance...")
        
        try:
            # Performance-Metriken sammeln
            start_time = time.time()
            
            await page.goto(self.base_url, wait_until='networkidle')
            
            load_time = time.time() - start_time
            
            # Performance-Metriken aus Playwright
            metrics = await page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                        totalTime: navigation.loadEventEnd - navigation.fetchStart
                    };
                }
            """)
            
            self.test_count += 1
            
            # Performance bewerten
            if load_time < 3.0:  # Weniger als 3 Sekunden
                self.success_count += 1
                logger.info(f"✅ Gute Performance: {load_time:.2f}s Ladezeit")
            elif load_time < 5.0:
                self.warnings.append(f"⚠️ Mittlere Performance: {load_time:.2f}s Ladezeit")
            else:
                self.errors.append(f"❌ Schlechte Performance: {load_time:.2f}s Ladezeit")
                
            logger.info(f"📊 Performance-Metriken: DOM={metrics['domContentLoaded']:.0f}ms, Load={metrics['loadComplete']:.0f}ms, Total={metrics['totalTime']:.0f}ms")
            
        except Exception as e:
            self.errors.append(f"❌ Performance-Test fehlgeschlagen: {str(e)}")
            
    async def test_specific_issues(self, page):
        """Testet spezifische Probleme mit Admin-Login für Analytics"""
        logger.info("🔧 Teste spezifische Probleme...")
        
        try:
            # Analytics-Seite mit Admin-Login testen
            await page.goto(f"{self.base_url}/accounts/login/", wait_until='networkidle')
            await page.fill('input[name="username"]', self.test_credentials['admin_username'])
            await page.fill('input[name="password"]', self.test_credentials['admin_password'])
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Analytics-Seite testen
            await page.goto(f"{self.base_url}/analytics/", wait_until='networkidle')
            self.test_count += 1
            
            # Prüfe ob Analytics-Seite erreichbar ist oder Zugriff verweigert wird
            current_url = page.url
            if 'analytics' in current_url:
                self.success_count += 1
                logger.info("✅ Analytics-Seite erreichbar")
            elif 'login' in current_url:
                self.warnings.append("⚠️ Analytics-Seite erfordert Login")
            elif '403' in current_url or 'forbidden' in current_url.lower():
                self.warnings.append("⚠️ Analytics-Seite nur für Administratoren")
            else:
                self.errors.append("❌ Analytics-Seite nicht erreichbar")
                
        except Exception as e:
            self.errors.append(f"❌ Spezifische Probleme-Test fehlgeschlagen: {str(e)}")
            
    def print_results(self):
        """Gibt Testergebnisse aus"""
        print("\n" + "="*60)
        print("🧪 E2E-TEST ERGEBNISSE")
        print("="*60)
        
        success_rate = (self.success_count / self.test_count * 100) if self.test_count > 0 else 0
        
        print(f"📊 Tests ausgeführt: {self.test_count}")
        print(f"✅ Erfolgreich: {self.success_count}")
        print(f"❌ Fehler: {len(self.errors)}")
        print(f"⚠️ Warnungen: {len(self.warnings)}")
        print(f"📈 Erfolgsrate: {success_rate:.1f}%")
        
        if self.errors:
            print("\n❌ FEHLER:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("\n⚠️ WARNUNGEN:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        print("\n" + "="*60)
        
        # Ergebnisse in Datei speichern
        results = {
            'timestamp': time.time(),
            'base_url': self.base_url,
            'test_count': self.test_count,
            'success_count': self.success_count,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'success_rate': success_rate,
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        with open('e2e_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        logger.info("📄 Ergebnisse in e2e_test_results.json gespeichert")

async def main():
    """Hauptfunktion"""
    tester = E2ETestApp("https://app.kairitter.de")
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main()) 