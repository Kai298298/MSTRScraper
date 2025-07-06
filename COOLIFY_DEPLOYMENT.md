# 🚀 Coolify Deployment - MaStR Lead Generator

## ✅ Einfaches GitHub + Coolify Deployment

Für das Deployment über GitHub und Coolify brauchst du **kein Docker**! Coolify kann die Anwendung direkt aus dem GitHub-Repository deployen.

## 📋 Coolify-Konfiguration

### 1. Repository in Coolify verbinden
- GitHub-Repository: `your-username/MSTRScraper`
- Branch: `main` oder `master`
- Build Command: `pip install -r requirements_deployment.txt`
- Start Command: `python manage.py runserver 0.0.0.0:$PORT --settings=data_visualizer.production_settings`

### 2. Umgebungsvariablen in Coolify setzen

#### Erforderliche Variablen:
```bash
DJANGO_SETTINGS_MODULE=data_visualizer.production_settings
DEBUG=False
SECRET_KEY=@*q(-up3f(d&rvc4s4it3%l04rnm@05b_^6n@3=kf4@&d-#vf2
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=http://your-domain.com
SITE_URL=http://your-domain.com
# SSL wird von Coolify übernommen - keine zusätzlichen SSL-Einstellungen nötig
```

#### E-Mail-Konfiguration:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

#### Datenbank (Coolify PostgreSQL):
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

#### Redis (optional):
```bash
REDIS_URL=redis://host:port/1
```

### 3. Build-Schritte in Coolify

#### Pre-Build Commands:
```bash
# Python-Abhängigkeiten installieren (verwendet requirements_deployment.txt)
pip install -r requirements_deployment.txt

# Datenbank-Migrationen
python manage.py migrate --settings=data_visualizer.production_settings

# Statische Dateien sammeln
python manage.py collectstatic --noinput --settings=data_visualizer.production_settings

# Superuser erstellen (falls nicht vorhanden)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser admin erstellt')
else:
    print('Superuser admin existiert bereits')
" --settings=data_visualizer.production_settings
```

#### Start Command:
```bash
python manage.py runserver 0.0.0.0:$PORT --settings=data_visualizer.production_settings
```

## 🔧 Produktions-Settings

Die `data_visualizer/production_settings.py` ist bereits für Coolify optimiert:

- ✅ Umgebungsvariablen-Support
- ✅ PostgreSQL-Support über `DATABASE_URL`
- ✅ Redis-Cache-Support
- ✅ Sichere Einstellungen (DEBUG=False, SSL, etc.)
- ✅ E-Mail-Konfiguration über Umgebungsvariablen

## 🌐 Domain-Konfiguration

### SSL/HTTPS
Coolify übernimmt automatisch:
- SSL-Zertifikate (Let's Encrypt)
- HTTPS-Redirects
- HSTS-Header

**Wichtig:** Die Django-SSL-Einstellungen sind deaktiviert, damit Coolify die SSL-Verwaltung übernehmen kann.

### Custom Domain
- Domain in Coolify hinzufügen
- DNS-Records entsprechend setzen
- `ALLOWED_HOSTS` und `CSRF_TRUSTED_ORIGINS` anpassen

## 📊 Monitoring

### Health Check
Coolify kann automatisch prüfen:
- URL: `/health/` (falls implementiert)
- Port: `$PORT`

### Logs
- Coolify zeigt automatisch Django-Logs
- Logs sind in `logs/django.log` und `logs/security.log`

## 🚨 Wichtige Hinweise

### ✅ Deployment-Problem behoben
Das bekannte Problem mit `django-compressor` wurde behoben:
- `django-compressor` wurde aus den Requirements entfernt
- `requirements_deployment.txt` enthält exakte, getestete Versionen
- Keine problematischen Testdateien mehr

### Vor dem ersten Deployment:
1. **SECRET_KEY** generieren und in Coolify setzen
2. **E-Mail-Einstellungen** konfigurieren
3. **Domain** in Coolify hinzufügen
4. **Umgebungsvariablen** alle setzen
5. **requirements_deployment.txt** verwenden (nicht requirements.txt)

### Nach dem Deployment:
1. **Admin-Account** testen: `/admin/` (admin/admin123)
2. **E-Mail-Verifikation** testen
3. **SSL/HTTPS** prüfen
4. **Performance** überwachen

## 🎯 Vorteile des direkten Deployments

- ✅ **Einfacher** - Kein Docker nötig
- ✅ **Schneller** - Direktes Python-Deployment
- ✅ **Weniger Konfiguration** - Coolify übernimmt vieles
- ✅ **Automatische Updates** - Bei GitHub-Push
- ✅ **SSL/HTTPS** - Automatisch von Coolify
- ✅ **Monitoring** - Integriert in Coolify

## 📞 Support

Bei Problemen:
1. **Coolify-Logs** prüfen
2. **Umgebungsvariablen** kontrollieren
3. **Django-Logs** in `logs/` anschauen
4. **Datenbank-Verbindung** testen

---

**Status:** ✅ Bereit für Coolify-Deployment
**Docker:** ❌ Nicht benötigt
**Komplexität:** 🟢 Einfach 