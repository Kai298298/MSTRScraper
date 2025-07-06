# 🚀 Automatische Test-Accounts

## ✅ Fertig! Sie müssen nichts mehr tun!

Die Test-Accounts werden jetzt **automatisch** beim Django-Start erstellt.

## 📋 Verfügbare Accounts

| Account | Username | Password | Typ |
|---------|----------|----------|-----|
| 🔑 Admin | `admin` | `admin123` | Superuser |
| 👤 Test | `testuser` | `testpass123` | Normaler User |

## 🎯 Wie es funktioniert

1. **Lokal:** `python manage.py runserver` → Accounts werden automatisch erstellt
2. **Produktion:** Coolify Deployment → Accounts werden automatisch erstellt
3. **Migration:** `python manage.py migrate` → Fehlende Accounts werden ergänzt

## 🔧 Technische Umsetzung

- **Django-Signals** in `accounts/signals.py`
- **App-Config** in `accounts/apps.py` 
- **Post-Migration-Hooks** für sichere Ausführung
- **Idempotente Logik** - verhindert Duplikate

## 📝 Logs

Die automatische Erstellung wird in den Django-Logs protokolliert:

```
🚀 Accounts-App bereit - Test-Accounts werden automatisch erstellt
🔧 Erstelle automatisch Test-Accounts...
✅ Admin-Account 'admin' automatisch erstellt
✅ Test-User 'testuser' automatisch erstellt
🎉 Test-Accounts Setup abgeschlossen!
```

## ⚠️ Sicherheitshinweis

Diese Accounts sind nur für **Entwicklung und Tests** gedacht!
In der Produktion sollten sichere Passwörter verwendet werden.

---

**Das war's! Die Test-Accounts funktionieren jetzt automatisch.** 🎉 