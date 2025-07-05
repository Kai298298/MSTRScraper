# 🚀 MaStR Lead Generator

Ein modernes Django-basiertes Tool zur Analyse und Visualisierung von MaStR-Daten (Marktstammdatenregister).

## 🎯 Features

- **Datenanalyse**: Umfassende Analyse von MaStR-Daten
- **Visualisierung**: Interaktive Karten und Charts
- **User Management**: Registrierung und Login-System
- **Subscription System**: Premium-Features mit Stripe
- **API**: RESTful API für Datenzugriff
- **Security**: Moderne Sicherheitsstandards

## 🛠️ Technologie-Stack

- **Backend**: Django 5.2, Python 3.11
- **Frontend**: Bootstrap 5, Leaflet Maps
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Cache**: Redis
- **Payment**: Stripe
- **Deployment**: Gunicorn, Nginx

## 🚀 Quick Start

### Lokale Entwicklung

```bash
# Repository klonen
git clone <repository-url>
cd version2

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\\Scripts\\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Environment konfigurieren
cp env_example.txt .env
# .env Datei bearbeiten

# Datenbank-Migrationen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Server starten
python manage.py runserver
```

## 🌐 Production Deployment

Das Projekt ist für verschiedene Deployment-Optionen optimiert. Siehe `docs/` für detaillierte Anweisungen.

### Voraussetzungen

- Web Server (Nginx/Apache)
- PostgreSQL Database
- Redis Cache
- Domain mit SSL

### Deployment

1. Environment Variables konfigurieren
2. Database und Cache einrichten
3. Static Files sammeln
4. Gunicorn starten

## 📁 Projektstruktur

```
version2/
├── accounts/           # User Management
├── dashboard/          # Hauptanwendung
├── subscriptions/      # Payment System
├── data_visualizer/    # Django Settings
├── templates/          # HTML Templates
├── static/            # Static Files
├── docs/              # Dokumentation
├── requirements.txt   # Dependencies
└── manage.py          # Django Management
```

## 🔒 Sicherheit

- HTTPS/SSL Enforcement
- CSRF Protection
- XSS Protection
- Rate Limiting
- Secure Headers
- Password Validation
- SQL Injection Protection

## 📊 Monitoring

- Health Check Endpoint: `/health/`
- Structured Logging
- Error Tracking (Sentry)
- Performance Monitoring

## 🧪 Testing

```bash
# Unit Tests
python manage.py test

# Code Quality
flake8 dashboard/ accounts/ subscriptions/
black --check dashboard/ accounts/ subscriptions/
```

## 📞 Support

Bei Fragen oder Problemen:
1. Dokumentation in `docs/` prüfen
2. Logs in `logs/` analysieren
3. Health Check testen

## 📄 Lizenz

Proprietär - Alle Rechte vorbehalten

---

**Entwickelt mit ❤️ für die Energiewende**
