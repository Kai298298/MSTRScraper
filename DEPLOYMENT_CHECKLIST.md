# ✅ Deployment-Checkliste - MaStR Lead Generator

## 🎯 Status: BEREIT FÜR DEPLOYMENT

Alle Probleme wurden behoben. Das Projekt kann jetzt über Git + Coolify deployed werden.

## 📋 Pre-Deployment Checkliste

### ✅ Code-Basis
- [ ] `django-compressor` entfernt
- [ ] `requirements_deployment.txt` erstellt
- [ ] `production_settings.py` konfiguriert
- [ ] `.gitignore` optimiert
- [ ] Alle Änderungen committed

### ✅ Repository
- [ ] GitHub Repository erstellt
- [ ] Code gepusht: `git push origin main`
- [ ] Branch: `main` oder `master`
- [ ] Keine sensiblen Daten im Repository

### ✅ Coolify-Konfiguration
- [ ] Coolify-Instanz verfügbar
- [ ] GitHub-Integration aktiviert
- [ ] Repository in Coolify verbunden

## 🚀 Deployment-Schritte

### 1. Coolify Anwendung erstellen
```bash
# In Coolify:
1. "New Application" → "Source: GitHub"
2. Repository auswählen: your-username/MSTRScraper
3. Branch: main
4. Build Command: pip install -r requirements_deployment.txt
5. Start Command: python manage.py runserver 0.0.0.0:$PORT --settings=data_visualizer.production_settings
```

### 2. Pre-Build Commands setzen
```bash
pip install -r requirements_deployment.txt
python manage.py migrate --settings=data_visualizer.production_settings
python manage.py collectstatic --noinput --settings=data_visualizer.production_settings
```

### 3. Umgebungsvariablen setzen (KRITISCH)
```bash
# Basis (MUSS gesetzt werden)
DJANGO_SETTINGS_MODULE=data_visualizer.production_settings
DEBUG=False
SECRET_KEY=dein-super-geheimer-schluessel-hier

# HTTPS-Konfiguration (WICHTIG für SSL)
ALLOWED_HOSTS=deine-domain.com,www.deine-domain.com
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com
SITE_URL=https://deine-domain.com

# Datenbank (Coolify PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# E-Mail (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=deine-email@gmail.com
EMAIL_HOST_PASSWORD=dein-app-passwort
DEFAULT_FROM_EMAIL=deine-email@gmail.com
```

### 4. Domain und SSL konfigurieren
- [ ] Custom Domain in Coolify hinzufügen
- [ ] DNS-Records setzen (A-Record auf Coolify-IP)
- [ ] SSL aktivieren (Let's Encrypt automatisch)
- [ ] "Force HTTPS" in Coolify aktivieren
- [ ] 5-10 Minuten warten für SSL-Zertifikat

### 5. Deploy starten
- [ ] "Deploy" Button klicken
- [ ] Build-Prozess überwachen
- [ ] Logs prüfen

## ✅ Post-Deployment Tests

### 🔍 Funktionalität testen
- [ ] Hauptseite lädt: `https://deine-domain.com/`
- [ ] Admin-Interface: `https://deine-domain.com/admin/`
- [ ] Login funktioniert: admin / admin123
- [ ] Betreiber-Seite: `https://deine-domain.com/betreiber/`
- [ ] Anlagen-Listen: `https://deine-domain.com/anlagen-listen/`

### 🔒 Sicherheit prüfen
- [ ] HTTPS aktiviert (grünes Schloss im Browser)
- [ ] HTTP → HTTPS Redirect funktioniert
- [ ] SSL-Zertifikat gültig (Let's Encrypt)
- [ ] Keine Mixed Content Warnungen
- [ ] CSRF-Fehler sind weg
- [ ] Security Headers gesetzt
- [ ] Keine Debug-Informationen sichtbar

### 📊 Performance prüfen
- [ ] Seiten laden schnell
- [ ] Statische Dateien werden geladen
- [ ] Datenbank-Verbindung funktioniert
- [ ] Logs zeigen keine Fehler

## 🚨 Troubleshooting

### Build-Fehler
```bash
# Problem: requirements_deployment.txt nicht gefunden
# Lösung: Stelle sicher, dass die Datei im Repository ist
git add requirements_deployment.txt
git commit -m "Add requirements_deployment.txt"
git push origin main
```

### DisallowedHost-Fehler
```bash
# Problem: Invalid HTTP_HOST header
# Lösung: ALLOWED_HOSTS in Coolify erweitern
# Value: hsgkccss4w88s4k0cocwgwoo.5.181.48.221.sslip.io,deine-domain.com
# Dann: Redeploy in Coolify
```

### Runtime-Fehler
```bash
# Problem: Umgebungsvariablen nicht gesetzt
# Lösung: Alle Variablen in Coolify prüfen
# Besonders: SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL
```

### SSL-Probleme
```bash
# Problem: SSL nicht aktiviert
# Lösung: Coolify übernimmt SSL automatisch
# Django-SSL-Einstellungen sind deaktiviert
```

### Datenbank-Probleme
```bash
# Problem: Datenbank-Verbindung fehlschlägt
# Lösung: DATABASE_URL in Coolify prüfen
# PostgreSQL muss in Coolify konfiguriert sein
```

## 📞 Support

### Logs prüfen
- **Coolify-Logs**: In der Coolify-Oberfläche
- **Django-Logs**: `logs/django.log` (falls verfügbar)
- **Build-Logs**: In Coolify unter "Builds"

### Häufige Probleme
1. **DisallowedHost-Fehler** - ALLOWED_HOSTS erweitern
2. **Umgebungsvariablen** nicht gesetzt
3. **SECRET_KEY** nicht generiert
4. **ALLOWED_HOSTS** nicht angepasst
5. **DATABASE_URL** falsch konfiguriert

## 🎉 Erfolg!

### ✅ Deployment erfolgreich wenn:
- [ ] Anwendung auf Domain erreichbar
- [ ] SSL/HTTPS aktiviert
- [ ] Admin-Interface funktioniert
- [ ] Alle Seiten laden
- [ ] Keine Fehler in Logs

### 🔄 Automatische Updates
- [ ] Git-Push triggert automatisches Deployment
- [ ] Coolify baut automatisch neu
- [ ] Keine manuellen Schritte nötig

---

**Status:** ✅ BEREIT FÜR DEPLOYMENT  
**Komplexität:** 🟢 Einfach  
**Zeitaufwand:** ~10 Minuten  
**Docker:** ❌ Nicht benötigt 