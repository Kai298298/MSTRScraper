# 🚀 MaStR Lead Generator

Ein moderner Django-basierter Lead Generator für die MaStR-Datenbank mit erweiterten Filtern, Benutzerverwaltung und Premium-Features.

## ✨ Features

- 🔍 **Erweiterte MaStR-Suche** mit Filtern und Umkreissuche
- 👥 **Benutzerregistrierung** mit E-Mail-Verifikation
- 💰 **Premium-Subscription** mit 14-tägiger Testversion
- 📊 **Analytics-Dashboard** mit Statistiken
- 🗂️ **Anlagen-Management** mit Listen und Notizen
- 🏢 **Betreiber-Analyse** mit geografischer Verteilung
- 📱 **Responsive Design** für alle Geräte
- 🔒 **Sichere Produktionsumgebung** mit SSL/HTTPS

## 🚀 Schnellstart

### Entwicklung
```bash
# Repository klonen
git clone https://github.com/your-username/MSTRScraper.git
cd MSTRScraper

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank-Migrationen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Server starten
python manage.py runserver
```

### Produktion (Coolify)
```bash
# Repository zu GitHub pushen
git add .
git commit -m "Produktionsbereit"
git push origin main

# In Coolify konfigurieren (siehe COOLIFY_DEPLOYMENT.md)
```

## 📋 Coolify-Konfiguration

### Umgebungsvariablen
```bash
DJANGO_SETTINGS_MODULE=data_visualizer.production_settings
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=http://your-domain.com
DATABASE_URL=postgresql://user:password@host:port/database
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Build-Commands
```bash
# Pre-Build
pip install -r requirements.txt
python manage.py migrate --settings=data_visualizer.production_settings
python manage.py collectstatic --noinput --settings=data_visualizer.production_settings

# Start-Command
python manage.py runserver 0.0.0.0:$PORT --settings=data_visualizer.production_settings
```

## 🔧 Technische Details

- **Django 5.2.3** - Aktuelle stabile Version
- **SQLite/PostgreSQL** - Flexible Datenbankunterstützung
- **Bootstrap 5** - Modernes Responsive Design
- **Chart.js** - Interaktive Visualisierungen
- **Leaflet.js** - Kartenintegration
- **Redis** - Caching (optional)

## 📊 Admin-Zugang

- **URL:** `/admin/`
- **Benutzer:** `admin`
- **Passwort:** `admin123`

## 🔒 Sicherheit

- ✅ DEBUG = False in Produktion
- ✅ SSL/HTTPS aktiviert
- ✅ Sichere Cookies (HttpOnly, Secure, SameSite)
- ✅ CSRF-Schutz
- ✅ XSS-Schutz
- ✅ E-Mail-Verifikation
- ✅ Session-Sicherheit

## 📚 Dokumentation

- [COOLIFY_DEPLOYMENT.md](COOLIFY_DEPLOYMENT.md) - Detaillierte Coolify-Anleitung
- [PRODUCTION_READY.md](PRODUCTION_READY.md) - Produktions-Checkliste
- [PROJECT_FINAL_STATUS.md](PROJECT_FINAL_STATUS.md) - Vollständiger Projektstatus

## 🆘 Support

Bei Problemen:
1. **Coolify-Logs** prüfen
2. **Umgebungsvariablen** kontrollieren
3. **Django-Logs** in `logs/` anschauen
4. **Health-Check:** `/health/`

## 📄 Lizenz

Dieses Projekt ist für den internen Gebrauch bestimmt.

---

**Status:** ✅ Produktionsbereit  
**Version:** 1.0.0  
**Letzte Aktualisierung:** $(date)
