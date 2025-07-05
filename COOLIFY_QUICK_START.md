# 🚀 Coolify Quick Start - MaStR Lead Generator

## ✅ Sofortiges Deployment

### 1. Repository zu GitHub pushen
```bash
git add .
git commit -m "Coolify-kompatibel - SSL deaktiviert"
git push origin main
```

### 2. In Coolify konfigurieren

#### Repository verbinden:
- **GitHub Repository:** `your-username/MSTRScraper`
- **Branch:** `main`

#### Build-Commands:
```bash
# Build Command
pip install -r requirements.txt

# Pre-Build Commands (einzeln hinzufügen)
python manage.py migrate --settings=data_visualizer.production_settings
python manage.py collectstatic --noinput --settings=data_visualizer.production_settings
```

#### Start Command:
```bash
python manage.py runserver 0.0.0.0:$PORT --settings=data_visualizer.production_settings
```

### 3. Umgebungsvariablen setzen

#### Mindest-Konfiguration:
```bash
DJANGO_SETTINGS_MODULE=data_visualizer.production_settings
DEBUG=False
SECRET_KEY=@*q(-up3f(d&rvc4s4it3%l04rnm@05b_^6n@3=kf4@&d-#vf2
ALLOWED_HOSTS=your-coolify-domain.com
CSRF_TRUSTED_ORIGINS=http://your-coolify-domain.com
```

#### Optional (für vollständige Funktionalität):
```bash
# E-Mail (für Registrierung)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Datenbank (Coolify PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Domain konfigurieren
- **Custom Domain** in Coolify hinzufügen
- **SSL** wird automatisch von Coolify verwaltet
- **DNS** entsprechend setzen

## 🔧 Was wurde geändert?

### ✅ SSL/HTTPS deaktiviert
- `SECURE_SSL_REDIRECT = False`
- `SECURE_HSTS_SECONDS = 0`
- `SESSION_COOKIE_SECURE = False`
- `CSRF_COOKIE_SECURE = False`

### ✅ Coolify übernimmt SSL
- Automatische SSL-Zertifikate
- HTTPS-Redirects
- HSTS-Header

### ✅ Kompatible Einstellungen
- Umgebungsvariablen-Support
- Flexible Datenbank-Konfiguration
- Fallback auf SQLite

## 🚨 Wichtige Hinweise

### ✅ Funktioniert jetzt:
- Deployment ohne SSL-Konflikte
- Coolify-kompatible Konfiguration
- Automatische SSL-Verwaltung

### ⚠️ Nach dem Deployment:
1. **Admin-Account** testen: `/admin/` (admin/admin123)
2. **E-Mail-Verifikation** konfigurieren
3. **Datenbank** auf PostgreSQL migrieren (optional)

## 📞 Bei Problemen

### Logs prüfen:
- **Coolify-Logs** in der Coolify-Oberfläche
- **Django-Logs** in `logs/django.log`

### Häufige Probleme:
- **Port-Konflikte:** `$PORT` Variable verwenden
- **Datenbank:** `DATABASE_URL` setzen
- **Static Files:** Pre-Build Command prüfen

---

**Status:** ✅ Coolify-kompatibel  
**SSL:** ❌ Deaktiviert (Coolify übernimmt)  
**Deployment:** 🟢 Einfach 