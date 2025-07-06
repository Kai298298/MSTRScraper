# Test-Accounts Setup

## Übersicht

Das MSTRScraper-System verfügt über **automatische Test-Accounts**, die beim Django-Start automatisch erstellt werden. Diese funktionieren sowohl lokal als auch im Produktionssystem.

## 🚀 Automatische Erstellung

### Was passiert automatisch:
- ✅ **Beim Django-Start** werden Test-Accounts automatisch erstellt
- ✅ **Nach Migrationen** werden fehlende Accounts ergänzt
- ✅ **Idempotent** - kann mehrfach ausgeführt werden ohne Probleme
- ✅ **Produktionssicher** - funktioniert in Coolify und lokal

### Sie müssen nichts tun!
Die Test-Accounts werden automatisch erstellt, sobald Sie:
- Den Django-Server starten (`python manage.py runserver`)
- Eine Migration ausführen (`python manage.py migrate`)
- Das System in Coolify deployen

## Verfügbare Test-Accounts

### 🔑 Admin-Account
- **Username:** `admin`
- **Email:** `admin@mstrscraper.de`
- **Password:** `admin123`
- **Berechtigungen:** Superuser (alle Rechte)
- **Verwendung:** Admin-Panel, alle Funktionen

### 👤 Test-User-Account
- **Username:** `testuser`
- **Email:** `test@mstrscraper.de`
- **Password:** `testpass123`
- **Berechtigungen:** Normaler User
- **Verwendung:** Testen der Benutzerfunktionen

## Manuelle Commands (Optional)

Falls Sie die Accounts manuell erstellen möchten:

### 1. Alle Test-Accounts auf einmal erstellen
```bash
python manage.py setup_test_accounts
```

### 2. Nur Admin-Account erstellen
```bash
python manage.py create_admin_user
```

### 3. Nur Test-User erstellen
```bash
python manage.py create_test_user
```

## Automatische Einrichtung

### Lokale Entwicklung
```bash
# Einfach den Server starten - Accounts werden automatisch erstellt
source venv_new/bin/activate
python manage.py runserver
```

### Produktionssystem (Coolify)
Die Accounts werden automatisch beim Deployment erstellt. Keine manuellen Schritte erforderlich!

## Logs und Debugging

Die automatische Erstellung wird in den Django-Logs protokolliert:

```
🚀 Accounts-App bereit - Test-Accounts werden automatisch erstellt
🔧 Erstelle automatisch Test-Accounts...
✅ Admin-Account 'admin' automatisch erstellt
✅ Test-User 'testuser' automatisch erstellt
🎉 Test-Accounts Setup abgeschlossen!
📋 Verfügbare Accounts:
   🔑 Admin: admin / admin123
   👤 Test: testuser / testpass123
```

## Sicherheitshinweise

⚠️ **Wichtig:** Diese Test-Accounts sind nur für Entwicklungs- und Testzwecke gedacht!

- Die Passwörter sind fest codiert und nicht sicher
- In einer echten Produktionsumgebung sollten diese Accounts deaktiviert werden
- Für echte Benutzer sollten sichere Passwörter verwendet werden

## Troubleshooting

### Accounts werden nicht erstellt
1. Prüfen Sie die Django-Logs auf Fehlermeldungen
2. Führen Sie manuell aus: `python manage.py setup_test_accounts`
3. Prüfen Sie ob die Datenbank bereit ist: `python manage.py check`

### Passwort-Reset
Falls die Passwörter geändert wurden:
```bash
python manage.py setup_test_accounts
```

### Datenbank-Probleme
```bash
python manage.py migrate
python manage.py setup_test_accounts
```

## Technische Details

### Automatische Erstellung funktioniert durch:
1. **Django-Signals** in `accounts/signals.py`
2. **App-Config** in `accounts/apps.py`
3. **Post-Migration-Hook** für sichere Ausführung
4. **Idempotente Logik** - verhindert Duplikate

### Integration in CI/CD
Die automatische Erstellung funktioniert in allen Deployment-Szenarien:
- Lokale Entwicklung
- Coolify Deployment
- Docker Container
- CI/CD Pipelines 