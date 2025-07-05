# 🚀 MaStR Lead Generator - Coolify Deployment Guide

## 📋 Voraussetzungen

- Coolify Server eingerichtet
- Domain/Subdomain konfiguriert
- SSL-Zertifikat verfügbar
- PostgreSQL Datenbank (kann Coolify bereitstellen)
- Redis Cache (kann Coolify bereitstellen)

## 🔧 Schritt-für-Schritt Deployment

### 1. Repository vorbereiten

Stelle sicher, dass folgende Dateien im Repository vorhanden sind:
- `Dockerfile`
- `requirements.txt`
- `docker-compose.yml`
- `nginx.conf`
- `.dockerignore`
- `env_example.txt`

### 2. Environment Variables in Coolify

Erstelle folgende Environment Variables in Coolify:

```bash
# Django Core
DEBUG=False
SECRET_KEY=dein-super-geheimer-schlüssel-hier
ALLOWED_HOSTS=deine-domain.com,www.deine-domain.com

# Database (wird von Coolify bereitgestellt)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis (wird von Coolify bereitgestellt)
REDIS_URL=redis://host:6379/0

# HTTPS Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_FRAME_DENY=True
X_FRAME_OPTIONS=DENY

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_COOKIE_AGE=3600

# CSRF Protection
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
CSRF_COOKIE_SAMESITE=Lax
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com

# Rate Limiting
RATELIMIT_ENABLE=True
RATELIMIT_USE_CACHE=default
MAX_REQUESTS_PER_DAY=1000
MAX_REQUESTS_PER_MINUTE=60

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.deine-domain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@deine-domain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@deine-domain.com

# Stripe Configuration (optional)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### 3. Coolify Application erstellen

1. **Neue Application erstellen**
   - Name: `mastr-lead-generator`
   - Source: GitHub/GitLab Repository
   - Branch: `main` oder `master`

2. **Build Configuration**
   - Build Command: `docker build -t mastr-lead-generator .`
   - Start Command: `gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 data_visualizer.wsgi:application`
   - Port: `8000`

3. **Resources**
   - CPU: 1-2 Cores
   - RAM: 2-4 GB
   - Storage: 10-20 GB

### 4. Database Setup

1. **PostgreSQL Database erstellen**
   - Coolify → Resources → Database
   - Type: PostgreSQL
   - Version: 15
   - Name: `mastr_db`

2. **Database URL in Environment Variables setzen**
   - Coolify stellt automatisch die DATABASE_URL bereit

### 5. Redis Setup

1. **Redis Cache erstellen**
   - Coolify → Resources → Cache
   - Type: Redis
   - Version: 7

2. **Redis URL in Environment Variables setzen**
   - Coolify stellt automatisch die REDIS_URL bereit

### 6. Domain & SSL

1. **Domain konfigurieren**
   - Domain: `deine-domain.com`
   - Subdomain: `mastr` (optional)

2. **SSL-Zertifikat**
   - Coolify kann automatisch Let's Encrypt Zertifikate bereitstellen
   - Oder eigenes Zertifikat hochladen

### 7. Deployment starten

1. **Build & Deploy**
   - Coolify → Deploy
   - Warte auf erfolgreichen Build

2. **Migrationen ausführen**
   ```bash
   # Über Coolify Terminal oder SSH
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

### 8. Post-Deployment Setup

1. **Superuser erstellen**
   ```bash
   python manage.py createsuperuser
   ```

2. **Statische Dateien sammeln**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Health Check testen**
   - URL: `https://deine-domain.com/health/`
   - Sollte `{"status": "healthy"}` zurückgeben

## 🔒 Sicherheitscheckliste

- [ ] SECRET_KEY geändert
- [ ] DEBUG=False gesetzt
- [ ] ALLOWED_HOSTS konfiguriert
- [ ] HTTPS aktiviert
- [ ] SSL-Zertifikat installiert
- [ ] Database-Passwort sicher
- [ ] Email-Konfiguration getestet
- [ ] Rate Limiting aktiv
- [ ] Security Headers gesetzt

## 📊 Monitoring & Logs

### Logs anzeigen
- Coolify → Application → Logs
- Real-time Logs verfügbar

### Health Monitoring
- URL: `/health/` für Health Checks
- Coolify automatisches Monitoring

### Performance Monitoring
- Coolify Resource Usage
- Application Response Times
- Database Performance

## 🚨 Troubleshooting

### Häufige Probleme

1. **Build fehlschlägt**
   - Prüfe `requirements.txt`
   - Prüfe `Dockerfile`
   - Prüfe Logs in Coolify

2. **Database Connection Error**
   - Prüfe DATABASE_URL
   - Prüfe Database Status in Coolify
   - Prüfe Firewall-Einstellungen

3. **Static Files nicht geladen**
   - Führe `collectstatic` aus
   - Prüfe STATIC_ROOT Konfiguration
   - Prüfe nginx.conf

4. **SSL/HTTPS Probleme**
   - Prüfe SSL-Zertifikat
   - Prüfe Domain-Konfiguration
   - Prüfe Security Headers

### Debug Commands

```bash
# Logs anzeigen
docker logs container-name

# Shell öffnen
docker exec -it container-name bash

# Django Shell
python manage.py shell

# Database Check
python manage.py check --deploy
```

## 🔄 Updates & Maintenance

### Code Updates
1. Push zu Repository
2. Coolify automatisches Rebuild
3. Zero-downtime Deployment

### Database Backups
- Coolify automatische Backups
- Manuelle Backups möglich
- Backup-Retention konfigurierbar

### SSL Renewal
- Let's Encrypt: Automatisch
- Eigene Zertifikate: Manuell erneuern

## 📞 Support

Bei Problemen:
1. Coolify Logs prüfen
2. Django Logs prüfen
3. Health Check URL testen
4. Database Connection testen
5. SSL-Zertifikat prüfen

---

**Viel Erfolg beim Deployment! 🚀** 