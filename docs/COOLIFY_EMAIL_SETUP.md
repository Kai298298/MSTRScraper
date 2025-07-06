# E-Mail-Konfiguration in Coolify

## Problem
Die E-Mail-Verifikation funktioniert nicht in der Produktion, weil die SMTP-Credentials nicht korrekt konfiguriert sind.

## Lösung

### 1. Umgebungsvariablen in Coolify setzen

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

### 2. Gmail App-Passwort erstellen

Falls Sie Gmail verwenden:

1. Gehen Sie zu [Google Account Settings](https://myaccount.google.com/)
2. Wählen Sie "Sicherheit"
3. Aktivieren Sie "2-Schritt-Verifizierung" falls noch nicht geschehen
4. Gehen Sie zu "App-Passwörter"
5. Erstellen Sie ein neues App-Passwort für "Django"
6. Verwenden Sie dieses Passwort als `EMAIL_HOST_PASSWORD`

### 3. Testen der E-Mail-Konfiguration

Nach dem Deployment können Sie die E-Mail-Funktionalität testen:

```bash
# In Coolify Console oder lokal mit Produktions-Settings
python manage.py test_email test@example.com
```

### 4. Überprüfung der Logs

Die Anwendung zeigt in den Logs an, welches E-Mail-Backend verwendet wird:

- **SMTP aktiviert**: `📧 SMTP-E-Mail konfiguriert: smtp.gmail.com:587`
- **Console-Backend**: `⚠️ E-Mail-Backend auf Console gesetzt`

### 5. Häufige Probleme

#### E-Mails kommen nicht an
- Prüfen Sie die SMTP-Credentials
- Stellen Sie sicher, dass `EMAIL_HOST_PASSWORD` nicht `your-email-password` ist
- Prüfen Sie die Firewall-Einstellungen

#### Gmail-Fehler
- Verwenden Sie App-Passwörter, nicht Ihr normales Passwort
- Stellen Sie sicher, dass 2FA aktiviert ist

#### Port-Probleme
- Port 587 (TLS) ist Standard
- Port 465 (SSL) erfordert `EMAIL_USE_SSL = True`

### 6. Alternative: SendGrid

Für bessere E-Mail-Zustellung können Sie SendGrid verwenden:

```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=ihr-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@ihre-domain.de
```

### 7. Sicherheitshinweise

- Verwenden Sie niemals echte Passwörter in den Logs
- Rotieren Sie App-Passwörter regelmäßig
- Verwenden Sie dedizierte E-Mail-Accounts für Produktionssysteme

## Nächste Schritte

1. Setzen Sie die Umgebungsvariablen in Coolify
2. Deployen Sie die Anwendung neu
3. Testen Sie die Registrierung mit einer echten E-Mail-Adresse
4. Prüfen Sie die Coolify-Logs auf E-Mail-Aktivität 