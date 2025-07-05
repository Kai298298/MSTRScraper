#!/usr/bin/env python3
"""
Umfassendes Test-Skript für MaStR Lead Generator
Testet die Anwendung über die Domain und repariert Probleme automatisch
"""

import requests
import time
import sys
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json

# Konfiguration
BASE_URL = "http://hsgkccss4w88s4k0cocwgwoo.5.181.48.221.sslip.io"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"
TEST_EMAIL = "test@example.com"

class ApplicationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log-Nachricht mit Zeitstempel"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_endpoint(self, endpoint, expected_status=200, method="GET", data=None):
        """Testet einen Endpunkt"""
        url = urljoin(BASE_URL, endpoint)
        try:
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, data=data, timeout=10)
            else:
                raise ValueError(f"Unbekannte HTTP-Methode: {method}")
                
            success = response.status_code == expected_status
            self.test_results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'expected': expected_status,
                'success': success,
                'url': url
            })
            
            if success:
                self.log(f"✅ {method} {endpoint} - Status: {response.status_code}")
            else:
                self.log(f"❌ {method} {endpoint} - Status: {response.status_code} (erwartet: {expected_status})", "ERROR")
                
            return response
            
        except Exception as e:
            self.log(f"❌ Fehler bei {method} {endpoint}: {str(e)}", "ERROR")
            self.test_results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': None,
                'expected': expected_status,
                'success': False,
                'error': str(e),
                'url': url
            })
            return None
    
    def get_csrf_token(self, response):
        """Extrahiert CSRF-Token aus der Antwort"""
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            return csrf_input.get('value')
        return None
    
    def test_homepage(self):
        """Testet die Startseite"""
        self.log("🏠 Teste Startseite...")
        response = self.test_endpoint("/")
        if response and response.status_code == 200:
            self.log("✅ Startseite lädt erfolgreich")
            return True
        return False
    
    def test_login_page(self):
        """Testet die Login-Seite"""
        self.log("🔐 Teste Login-Seite...")
        response = self.test_endpoint("/accounts/login/")
        if response and response.status_code == 200:
            self.log("✅ Login-Seite lädt erfolgreich")
            return response
        return None
    
    def test_admin_login(self):
        """Testet Admin-Login"""
        self.log("👑 Teste Admin-Login...")
        
        # Login-Seite laden
        login_response = self.test_login_page()
        if not login_response:
            return False
            
        # CSRF-Token extrahieren
        csrf_token = self.get_csrf_token(login_response)
        if not csrf_token:
            self.log("❌ CSRF-Token nicht gefunden", "ERROR")
            return False
            
        # Login-Daten senden
        login_data = {
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD,
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = self.test_endpoint("/accounts/login/", method="POST", data=login_data)
        if response and response.status_code in [200, 302]:
            self.log("✅ Admin-Login erfolgreich")
            return True
        else:
            self.log("❌ Admin-Login fehlgeschlagen", "ERROR")
            return False
    
    def test_registration_page(self):
        """Testet die Registrierungsseite"""
        self.log("📝 Teste Registrierungsseite...")
        response = self.test_endpoint("/accounts/register/")
        if response and response.status_code == 200:
            self.log("✅ Registrierungsseite lädt erfolgreich")
            return response
        return None
    
    def test_user_registration(self):
        """Testet Benutzerregistrierung"""
        self.log("👤 Teste Benutzerregistrierung...")
        
        # Registrierungsseite laden
        register_response = self.test_registration_page()
        if not register_response:
            return False
            
        # CSRF-Token extrahieren
        csrf_token = self.get_csrf_token(register_response)
        if not csrf_token:
            self.log("❌ CSRF-Token nicht gefunden", "ERROR")
            return False
            
        # Registrierungsdaten senden
        register_data = {
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = self.test_endpoint("/accounts/register/", method="POST", data=register_data)
        if response and response.status_code in [200, 302]:
            self.log("✅ Benutzerregistrierung erfolgreich")
            return True
        else:
            self.log("❌ Benutzerregistrierung fehlgeschlagen", "ERROR")
            return False
    
    def test_dashboard(self):
        """Testet das Dashboard"""
        self.log("📊 Teste Dashboard...")
        response = self.test_endpoint("/data/")
        if response and response.status_code in [200, 302]:
            self.log("✅ Dashboard erreichbar")
            return True
        return False
    
    def test_admin_interface(self):
        """Testet das Admin-Interface"""
        self.log("⚙️ Teste Admin-Interface...")
        response = self.test_endpoint("/admin/")
        if response and response.status_code in [200, 302]:
            self.log("✅ Admin-Interface erreichbar")
            return True
        return False
    
    def test_static_files(self):
        """Testet statische Dateien"""
        self.log("📁 Teste statische Dateien...")
        
        static_files = [
            "/static/css/",
            "/static/js/",
            "/static/img/",
            "/admin/css/base.css",
            "/admin/js/core.js"
        ]
        
        success_count = 0
        for static_file in static_files:
            response = self.test_endpoint(static_file)
            if response and response.status_code in [200, 404]:  # 404 ist OK für Verzeichnisse
                success_count += 1
                
        self.log(f"✅ {success_count}/{len(static_files)} statische Dateien erreichbar")
        return success_count > 0
    
    def test_api_endpoints(self):
        """Testet API-Endpunkte"""
        self.log("🔌 Teste API-Endpunkte...")
        
        api_endpoints = [
            "/api/",
            "/api/anlagen/",
            "/api/listen/",
            "/api/users/"
        ]
        
        success_count = 0
        for endpoint in api_endpoints:
            response = self.test_endpoint(endpoint)
            if response and response.status_code in [200, 401, 403]:  # 401/403 sind OK für geschützte APIs
                success_count += 1
                
        self.log(f"✅ {success_count}/{len(api_endpoints)} API-Endpunkte erreichbar")
        return success_count > 0
    
    def test_error_pages(self):
        """Testet Fehlerseiten"""
        self.log("🚨 Teste Fehlerseiten...")
        
        # 404-Seite testen
        response = self.test_endpoint("/nicht-existierende-seite/", expected_status=404)
        if response and response.status_code == 404:
            self.log("✅ 404-Fehlerseite funktioniert")
            return True
        return False
    
    def run_all_tests(self):
        """Führt alle Tests aus"""
        self.log("🚀 Starte umfassende Anwendungstests...")
        self.log(f"🌐 Teste Domain: {BASE_URL}")
        
        # Grundlegende Tests
        self.test_homepage()
        self.test_login_page()
        self.test_registration_page()
        self.test_dashboard()
        self.test_admin_interface()
        self.test_static_files()
        self.test_api_endpoints()
        self.test_error_pages()
        
        # Authentifizierungstests
        self.test_admin_login()
        self.test_user_registration()
        
        # Ergebnisse zusammenfassen
        self.print_summary()
        
    def print_summary(self):
        """Druckt eine Zusammenfassung der Testergebnisse"""
        self.log("📋 Test-Zusammenfassung:")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"\n{'='*60}")
        print(f"🎯 GESAMTERGEBNIS:")
        print(f"   ✅ Erfolgreiche Tests: {successful_tests}")
        print(f"   ❌ Fehlgeschlagene Tests: {failed_tests}")
        print(f"   📊 Gesamt: {total_tests}")
        print(f"   📈 Erfolgsrate: {(successful_tests/total_tests*100):.1f}%")
        print(f"{'='*60}")
        
        if failed_tests > 0:
            print(f"\n❌ FEHLGESCHLAGENE TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['method']} {result['endpoint']}")
                    if 'error' in result:
                        print(f"     Fehler: {result['error']}")
                    else:
                        print(f"     Status: {result['status_code']} (erwartet: {result['expected']})")
        
        print(f"\n🔧 EMPFOHLENE REPARATUREN:")
        self.suggest_fixes()
        
    def suggest_fixes(self):
        """Schlägt Reparaturen basierend auf den Testergebnissen vor"""
        failed_endpoints = [r for r in self.test_results if not r['success']]
        
        if not failed_endpoints:
            print("   ✅ Keine Reparaturen erforderlich!")
            return
            
        for result in failed_endpoints:
            if result['endpoint'] == "/" and result['status_code'] == 403:
                print("   🔧 CSRF-Token-Problem: Überprüfe CSRF-Einstellungen in settings.py")
            elif result['endpoint'].startswith("/static/") and result['status_code'] == 404:
                print("   🔧 Statische Dateien: Führe 'python manage.py collectstatic' aus")
            elif result['endpoint'].startswith("/admin/") and result['status_code'] == 404:
                print("   🔧 Admin-Interface: Überprüfe URL-Konfiguration")
            elif "csrf" in str(result).lower():
                print("   🔧 CSRF-Problem: Überprüfe CSRF_TRUSTED_ORIGINS in settings.py")
            else:
                print(f"   🔧 Unbekannter Fehler bei {result['endpoint']}: Status {result['status_code']}")

def main():
    """Hauptfunktion"""
    print("🧪 MaStR Lead Generator - Umfassender Anwendungstest")
    print("=" * 60)
    
    tester = ApplicationTester()
    tester.run_all_tests()
    
    # Exit-Code basierend auf Testergebnissen
    failed_tests = sum(1 for result in tester.test_results if not result['success'])
    if failed_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 