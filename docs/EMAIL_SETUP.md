# 📧 E-Mail-Konfiguration

## Problem: Bestätigungs-E-Mails kommen nicht an

Das Problem liegt daran, dass die E-Mail-Konfiguration für lokale Entwicklung auf "Console" eingestellt ist. E-Mails werden nur in der Konsole angezeigt, aber nicht wirklich versendet.

## 🔧 Lösungen

### Option 1: E-Mails in der Konsole anzeigen (Lokale Entwicklung)

**Aktueller Status:** ✅ Funktioniert bereits

Wenn Sie sich registrieren, werden die E-Mails in der Django-Konsole angezeigt:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 8bit
Subject: E-Mail-Adresse bestätigen - MaStR Lead Generator
From: noreply@mastr-leads.de
To: your-email@example.com

Hallo username,

vielen Dank für Ihre Registrierung beim MaStR Lead Generator!

Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Link klicken:

http://localhost:8000/accounts/verify-email/TOKEN_HIER/

Dieser Link ist 24 Stunden gültig.
```

**So verwenden Sie den Link:**
1. Kopieren Sie den Link aus der Konsole
2. Fügen Sie ihn in Ihren Browser ein
3. Ihr Konto wird aktiviert

### Option 2: Echte E-Mails versenden (Produktion)

#### Für Gmail:
```bash
# Umgebungsvariablen setzen
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-app-password"  # App-Passwort, nicht normales Passwort
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
```

#### Für andere E-Mail-Provider:
```bash
export EMAIL_HOST="smtp.your-provider.com"
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER="your-email@your-provider.com"
export EMAIL_HOST_PASSWORD="your-password"
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
```

### Option 3: Test-E-Mail senden

Testen Sie die E-Mail-Konfiguration:

```bash
python manage.py test_email your-email@example.com
```

## 🚀 Für Produktion (Coolify)

In der Produktion werden E-Mails automatisch versendet, wenn die Umgebungsvariablen in Coolify gesetzt sind:

### Umgebungsvariablen in Coolify setzen

Gehen Sie in Coolify zu Ihrem MSTRScraper-Projekt und fügen Sie folgende Umgebungsvariablen hinzu:

#### Für Gmail SMTP:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ihre-email@gmail.com
EMAIL_HOST_PASSWORD=ihr-app-passwort
DEFAULT_FROM_EMAIL=ihre-email@gmail.com
SITE_URL=https://app.kairitter.de
```

#### Für andere SMTP-Anbieter:
```
EMAIL_HOST=smtp.ihr-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ihre-email@ihr-provider.com
EMAIL_HOST_PASSWORD=ihr-passwort
DEFAULT_FROM_EMAIL=ihre-email@ihr-provider.com
SITE_URL=https://app.kairitter.de
```

### Testen in der Produktion

Nach dem Deployment können Sie die E-Mail-Funktionalität testen:

```bash
# In Coolify Console
python manage.py test_production_email test@example.com
```

### Überprüfung der Logs

Die Anwendung zeigt in den Logs an, welches E-Mail-Backend verwendet wird:

- **SMTP aktiviert**: `📧 SMTP-E-Mail konfiguriert: smtp.gmail.com:587`
- **Console-Backend**: `⚠️ E-Mail-Backend auf Console gesetzt`

## 📋 Gmail App-Passwort erstellen

1. Gehen Sie zu [Google Account Settings](https://myaccount.google.com/)
2. Sicherheit → 2-Schritt-Verifizierung aktivieren
3. App-Passwörter → Neues App-Passwort erstellen
4. Passwort kopieren und als `EMAIL_HOST_PASSWORD` verwenden

## 🔍 Troubleshooting

### E-Mails kommen nicht an:
1. **Spam-Ordner prüfen**
2. **E-Mail-Adresse korrekt geschrieben?**
3. **SMTP-Einstellungen korrekt?**
4. **Firewall blockiert Port 587?**

### Gmail-Fehler:
- **"Username and Password not accepted"**: App-Passwort verwenden, nicht normales Passwort
- **"Less secure app access"**: 2-Schritt-Verifizierung aktivieren

### Testen:
```bash
# E-Mail-Konfiguration prüfen
python manage.py test_email your-email@example.com

# Django-Server mit E-Mail-Logs starten
python manage.py runserver
```

## 📝 Aktuelle Konfiguration prüfen

```bash
python manage.py shell
```

```python
from django.conf import settings
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'Nicht gesetzt'}")
```

## ✅ Schnelle Lösung für lokale Tests

Für lokale Tests können Sie einfach:

1. **Registrierung durchführen**
2. **E-Mail-Link aus der Konsole kopieren**
3. **Link im Browser öffnen**
4. **Konto ist aktiviert**

Die E-Mail-Funktionalität funktioniert vollständig - nur der Versand ist für lokale Entwicklung auf Console umgestellt. 