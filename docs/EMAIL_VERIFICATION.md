# E-Mail-Verifikationssystem

## Übersicht

Das MaStR Lead Generator Projekt implementiert ein vollständiges E-Mail-Verifikationssystem für die Benutzerregistrierung. Dies erhöht die Sicherheit und stellt sicher, dass nur echte E-Mail-Adressen verwendet werden.

## Funktionsweise

### 1. Registrierungsprozess

1. **Benutzer registriert sich** über das Registrierungsformular
2. **Konto wird erstellt** aber als `is_active=False` markiert
3. **UserProfile wird erstellt** mit E-Mail-Verifikationsfeldern
4. **Verifikations-E-Mail wird gesendet** mit einem 24-Stunden-gültigen Token
5. **Benutzer wird zur Bestätigungsseite weitergeleitet**

### 2. E-Mail-Verifikation

1. **Benutzer klickt auf Link** in der Verifikations-E-Mail
2. **Token wird validiert** (24 Stunden Gültigkeit)
3. **Konto wird aktiviert** (`is_active=True`)
4. **Premium-Test wird gestartet** (14 Tage)
5. **Benutzer wird automatisch eingeloggt**

### 3. Fallback-Mechanismen

- **E-Mail nicht erhalten**: Link zur erneuten E-Mail-Sendung
- **Token abgelaufen**: Möglichkeit, neuen Token anzufordern
- **Falsche E-Mail**: Benutzer kann sich mit korrekter E-Mail neu registrieren

## Technische Implementierung

### Modelle

#### UserProfile
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Views

- `register()`: Registrierung mit E-Mail-Verifikation
- `verification_sent()`: Bestätigungsseite nach E-Mail-Versand
- `verify_email(token)`: E-Mail-Verifikation durch Token
- `resend_verification()`: Erneutes Senden der Verifikations-E-Mail
- `login_view()`: Erweiterte Login-View mit Verifikations-Check

### URLs

```python
urlpatterns = [
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]
```

### Templates

- `verification_sent.html`: Bestätigungsseite nach E-Mail-Versand
- `resend_verification.html`: Formular für erneute E-Mail-Sendung
- `register.html`: Erweitertes Registrierungsformular mit Hinweisen

## E-Mail-Konfiguration

### Settings
```python
# E-Mail-Einstellungen
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Für Entwicklung
EMAIL_HOST = 'smtp.example.com'  # Für Produktion
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@mastr-leads.de'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@mastr-leads.de'

# Site URL für E-Mail-Links
SITE_URL = 'https://your-domain.com'
```

### E-Mail-Template
Die Verifikations-E-Mail enthält:
- Persönliche Begrüßung
- Verifikationslink mit Token
- Gültigkeitsdauer (24 Stunden)
- Hinweise zur Sicherheit

## Sicherheitsfeatures

### Token-Sicherheit
- **64-Zeichen-Token**: Kryptographisch sichere Zufallszeichen
- **24-Stunden-Gültigkeit**: Automatische Ablaufzeit
- **Einmalverwendung**: Token wird nach Verifikation gelöscht

### Konto-Sicherheit
- **Inaktive Konten**: Neue Konten sind standardmäßig inaktiv
- **E-Mail-Validierung**: Nur verifizierte E-Mails können genutzt werden
- **Automatische Bereinigung**: Abgelaufene Token werden nicht akzeptiert

### Rate Limiting
- **E-Mail-Versand**: Begrenzung der E-Mail-Sendungen pro E-Mail-Adresse
- **Token-Generierung**: Verhinderung von Token-Spam
- **Login-Versuche**: Schutz vor Brute-Force-Angriffen

## Admin-Integration

### UserProfile Admin
- **Übersicht**: Alle Benutzer mit Verifikationsstatus
- **Filter**: Nach Verifikationsstatus und Onboarding
- **Aktionen**: Manuelle Verifikation und Token-Reset

### User Admin Erweiterung
- **Inline UserProfile**: Direkte Bearbeitung im User-Admin
- **Verifikationsstatus**: Anzeige des E-Mail-Verifikationsstatus
- **Bulk-Aktionen**: Massenverifikation von Konten

## Management-Commands

### create_user_profiles
```bash
python manage.py create_user_profiles
```
Erstellt UserProfile für bestehende Benutzer, die noch keines haben.

## Fehlerbehandlung

### Häufige Probleme

1. **E-Mail nicht erhalten**
   - Spam-Ordner überprüfen
   - E-Mail-Adresse korrekt geschrieben
   - Erneute E-Mail anfordern

2. **Token abgelaufen**
   - Neue Verifikations-E-Mail anfordern
   - 24-Stunden-Gültigkeit beachten

3. **Falsche E-Mail-Adresse**
   - Neues Konto mit korrekter E-Mail erstellen
   - Altes Konto kann gelöscht werden

### Logging
Alle E-Mail-Verifikationsaktivitäten werden geloggt:
- Erfolgreiche Verifikationen
- Fehlgeschlagene Versuche
- Token-Generierung
- E-Mail-Versand

## Produktions-Checkliste

### E-Mail-Server
- [ ] SMTP-Server konfiguriert
- [ ] E-Mail-Credentials gesetzt
- [ ] SPF/DKIM Records konfiguriert
- [ ] E-Mail-Deliverability getestet

### Domain-Konfiguration
- [ ] SITE_URL korrekt gesetzt
- [ ] HTTPS aktiviert
- [ ] SSL-Zertifikat gültig

### Monitoring
- [ ] E-Mail-Versand überwachen
- [ ] Verifikationsraten tracken
- [ ] Fehler-Logging aktiviert

## Testing

### Manuelle Tests
1. Registrierung mit gültiger E-Mail
2. E-Mail-Verifikation durch Klick
3. Erneute E-Mail-Sendung
4. Abgelaufene Token-Behandlung
5. Login mit unverifiziertem Konto

### Automatisierte Tests
```python
# Beispiel-Test
def test_email_verification(self):
    user = User.objects.create_user(username='test', email='test@example.com')
    profile = user.profile
    token = profile.generate_verification_token()
    
    # Token sollte gültig sein
    self.assertTrue(profile.is_verification_token_valid())
    
    # Verifikation sollte funktionieren
    self.assertTrue(profile.verify_email(token))
    self.assertTrue(profile.email_verified)
```

## Wartung

### Regelmäßige Aufgaben
- **Token-Bereinigung**: Abgelaufene Token entfernen
- **E-Mail-Logs**: Überprüfung der E-Mail-Deliverability
- **Verifikationsraten**: Monitoring der Erfolgsquoten

### Backup-Strategie
- **UserProfile-Daten**: Regelmäßige Backups
- **E-Mail-Templates**: Versionierung der E-Mail-Inhalte
- **Konfiguration**: Sichern der E-Mail-Einstellungen 