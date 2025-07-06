# E2E-Tests für MSTRScraper

Dieses Verzeichnis enthält umfassende End-to-End-Tests für die MSTRScraper-Anwendung.

## 📋 Übersicht

Die E2E-Tests verwenden **Playwright** und testen die vollständige Funktionalität der Anwendung, einschließlich:

- ✅ Verfügbarkeit und Performance
- ✅ Navigation und Routing
- ✅ Authentifizierung (Login/Registrierung/Logout)
- ✅ Dashboard-Funktionen
- ✅ Daten-Seiten (Suche, Filter, Kartenansicht)
- ✅ Responsive Design
- ✅ Spezifische Probleme (Analytics, etc.)

## 🚀 Installation

### 1. Playwright installieren

```bash
# Playwright und Browser installieren
pip install playwright
playwright install chromium
```

### 2. Test-Accounts erstellen

```bash
# Test-Accounts für E2E-Tests erstellen
python manage.py create_test_accounts
```

## 🧪 Tests ausführen

### Option 1: Lokale Tests (empfohlen)

```bash
# Vollständiger Test-Runner (erstellt Accounts, startet Server, führt Tests aus)
python tests/run_e2e_tests.py
```

### Option 2: Produktions-Tests

```bash
# Tests gegen die live-Anwendung auf https://app.kairitter.de/
python tests/e2e_test_app.py
```

### Option 3: Manueller Test

```bash
# Django-Server starten
python manage.py runserver 8000

# In neuem Terminal: Tests ausführen
python -c "
import asyncio
from tests.e2e_test_app import E2ETestApp

async def main():
    tester = E2ETestApp('http://localhost:8000')
    await tester.run_tests()

asyncio.run(main())
"
```

## 📊 Test-Accounts

Die Tests verwenden folgende Test-Accounts:

| Benutzer | Passwort | Rolle | Beschreibung |
|----------|----------|-------|--------------|
| `testuser` | `testpass123` | Premium-User | Normaler Benutzer mit Premium-Features |
| `admin` | `adminpass123` | Administrator | Admin-Account für Analytics-Tests |

## 🔧 Konfiguration

### Test-Parameter anpassen

In `tests/e2e_test_app.py` können Sie folgende Parameter anpassen:

```python
class E2ETestApp:
    def __init__(self, base_url="https://app.kairitter.de"):
        self.base_url = base_url
        self.headless = False        # Browser sichtbar machen
        self.slow_mo = 1000          # Verzögerung zwischen Aktionen (ms)
        self.screenshot_on_error = True  # Screenshots bei Fehlern
```

### Test-Credentials ändern

```python
self.test_credentials = {
    'username': 'ihr_testuser',
    'password': 'ihr_testpass',
    'admin_username': 'ihr_admin',
    'admin_password': 'ihr_adminpass'
}
```

## 📈 Testergebnisse

### Erfolgsrate

Die Tests zeigen eine Erfolgsrate basierend auf:
- ✅ Erfolgreiche Tests
- ❌ Kritische Fehler
- ⚠️ Warnungen

### Ergebnis-Datei

Nach jedem Testlauf wird eine JSON-Datei erstellt:
- `e2e_test_results.json` - Detaillierte Testergebnisse

### Beispiel-Output

```
🧪 E2E-TEST ERGEBNISSE
============================================================
📊 Tests ausgeführt: 25
✅ Erfolgreich: 22
❌ Fehler: 1
⚠️ Warnungen: 2
📈 Erfolgsrate: 88.0%

❌ FEHLER:
  • Analytics-Seite nicht erreichbar

⚠️ WARNUNGEN:
  • Karten-Tab/Button nicht gefunden
  • Logout-Link nicht gefunden
```

## 🔍 Bekannte Probleme

### 1. Karten-Tab nicht gefunden

**Problem:** Der Karten-Button wird nicht erkannt
**Lösung:** Prüfen Sie, ob die ID `#btn-card-view` im Template vorhanden ist

### 2. Logout-Link nicht sichtbar

**Problem:** Logout-Link ist im Dropdown-Menü versteckt
**Lösung:** Tests öffnen automatisch das Dropdown-Menü

### 3. Analytics-Seite nur für Admins

**Problem:** Analytics-Seite erfordert Admin-Rechte
**Lösung:** Tests verwenden automatisch Admin-Account

### 4. Keine Testdaten

**Problem:** Listen/Betreiber-Seiten zeigen keine Daten
**Lösung:** Tests prüfen auf "Keine Daten" Nachrichten

## 🛠️ Troubleshooting

### Browser-Probleme

```bash
# Browser neu installieren
playwright install --force chromium
```

### Django-Server-Probleme

```bash
# Port bereits belegt
python manage.py runserver 8001

# Oder Prozess beenden
lsof -ti:8000 | xargs kill -9
```

### Test-Accounts Probleme

```bash
# Test-Accounts neu erstellen
python manage.py create_test_accounts --force
```

## 📝 Test erweitern

### Neuen Test hinzufügen

```python
async def test_new_feature(self, page):
    """Testet neue Funktion"""
    logger.info("🔧 Teste neue Funktion...")
    
    try:
        # Test-Logik hier
        self.test_count += 1
        self.success_count += 1
        logger.info("✅ Neue Funktion funktioniert")
        
    except Exception as e:
        self.errors.append(f"❌ Neuer Test fehlgeschlagen: {str(e)}")
```

### Test in Hauptfunktion einbinden

```python
async def run_tests(self):
    # ... bestehende Tests ...
    
    # Neuen Test hinzufügen
    await self.test_new_feature(page)
```

## 🎯 Best Practices

1. **Robuste Selektoren:** Verwenden Sie mehrere Selektoren für wichtige Elemente
2. **Warten auf Elemente:** Verwenden Sie `wait_for_load_state()` für bessere Stabilität
3. **Fehlerbehandlung:** Fangen Sie Exceptions ab und dokumentieren Sie Warnungen
4. **Screenshots:** Aktivieren Sie Screenshots bei Fehlern für Debugging
5. **Testdaten:** Erstellen Sie ausreichend Testdaten für realistische Tests

## 📞 Support

Bei Problemen mit den Tests:

1. Prüfen Sie die Logs für detaillierte Fehlermeldungen
2. Aktivieren Sie `headless = False` für visuelle Inspektion
3. Erhöhen Sie `slow_mo` für langsamere Ausführung
4. Prüfen Sie die `e2e_test_results.json` für Details 