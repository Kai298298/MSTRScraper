# 🔒 SSL/HTTPS Konfiguration in Coolify - MaStR Lead Generator

## ✅ Coolify übernimmt SSL automatisch

Das Gute: **Du musst nichts manuell konfigurieren!** Coolify übernimmt die SSL-Verwaltung automatisch.

## 📋 Schritt-für-Schritt SSL-Einrichtung

### 1. Domain in Coolify hinzufügen

#### In Coolify Dashboard:
1. **Deine Anwendung** öffnen
2. **"Domains"** Tab klicken
3. **"Add Domain"** Button
4. **Deine Domain eingeben**:
   ```
   deine-domain.com
   www.deine-domain.com (optional)
   ```
5. **"Save"** klicken

### 2. SSL aktivieren

#### Automatische SSL-Konfiguration:
```bash
# Coolify macht das automatisch:
✅ SSL Certificate: Let's Encrypt (automatisch)
✅ Force HTTPS: Aktiviert
✅ HTTP → HTTPS Redirect: Aktiviert
✅ HSTS Headers: Aktiviert (optional)
```

#### Manuelle SSL-Optionen (falls benötigt):
```bash
# In Coolify unter "Domains" → "SSL Settings":
- Let's Encrypt (empfohlen, kostenlos)
- Custom Certificate (falls du eigene Zertifikate hast)
- Disabled (nicht empfohlen)
```

### 3. Umgebungsvariablen setzen

#### Basis-Konfiguration:
```bash
# MUSS gesetzt werden:
DJANGO_SETTINGS_MODULE=data_visualizer.production_settings
DEBUG=False
SECRET_KEY=dein-super-geheimer-schluessel-hier

# HTTPS-Konfiguration:
ALLOWED_HOSTS=deine-domain.com,www.deine-domain.com
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com
SITE_URL=https://deine-domain.com
```

#### Wichtige Hinweise:
- **CSRF_TRUSTED_ORIGINS** MUSS `https://` verwenden
- **SITE_URL** MUSS `https://` verwenden
- **ALLOWED_HOSTS** kann ohne Protokoll sein

### 4. DNS-Konfiguration

#### DNS-Records setzen:
```bash
# Bei deinem Domain-Provider:
Type: A
Name: @ (oder deine-domain.com)
Value: [Coolify Server IP]

Type: A
Name: www
Value: [Coolify Server IP]

# Oder CNAME für www:
Type: CNAME
Name: www
Value: deine-domain.com
```

## 🔧 Django SSL-Einstellungen

### ✅ Was Django macht:
```python
# In production_settings.py:
SECURE_SSL_REDIRECT = False  # Coolify übernimmt das
SECURE_HSTS_SECONDS = 0      # Coolify übernimmt das
SESSION_COOKIE_SECURE = False # Coolify übernimmt HTTPS
CSRF_COOKIE_SECURE = False    # Coolify übernimmt HTTPS
```

### ✅ Was Coolify macht:
- **SSL-Zertifikate** automatisch generieren
- **HTTP → HTTPS** Redirects
- **HSTS-Header** setzen
- **Security Headers** verwalten

## 🚨 Häufige Probleme und Lösungen

### Problem: "Mixed Content" Fehler
```bash
# Lösung: CSRF_TRUSTED_ORIGINS prüfen
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com
```

### Problem: SSL-Zertifikat wird nicht erstellt
```bash
# Lösung: DNS-Records prüfen
# Warte 5-10 Minuten nach DNS-Änderung
# Prüfe Coolify-Logs für SSL-Fehler
```

### Problem: HTTP funktioniert, HTTPS nicht
```bash
# Lösung: Coolify SSL-Einstellungen prüfen
# "Force HTTPS" sollte aktiviert sein
```

### Problem: CSRF-Fehler bei HTTPS
```bash
# Lösung: CSRF_TRUSTED_ORIGINS anpassen
CSRF_TRUSTED_ORIGINS=https://deine-domain.com
```

## 📊 SSL-Test

### Nach dem Deployment testen:
```bash
# 1. HTTP → HTTPS Redirect
http://deine-domain.com → sollte zu https://deine-domain.com weiterleiten

# 2. SSL-Zertifikat prüfen
https://deine-domain.com → sollte grünes Schloss zeigen

# 3. HSTS testen
curl -I https://deine-domain.com
# Sollte "Strict-Transport-Security" Header zeigen

# 4. Mixed Content prüfen
# Browser-Entwicklertools → Console → keine Mixed Content Warnungen
```

## 🎯 Best Practices

### ✅ Empfohlene Konfiguration:
```bash
# Umgebungsvariablen:
ALLOWED_HOSTS=deine-domain.com,www.deine-domain.com
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com
SITE_URL=https://deine-domain.com

# Coolify-Einstellungen:
✅ SSL: Let's Encrypt
✅ Force HTTPS: Enabled
✅ HSTS: Enabled (optional)
```

### ❌ Vermeiden:
- Django SSL-Einstellungen manuell aktivieren
- Eigene SSL-Zertifikate (außer du weißt was du tust)
- HTTP ohne Redirect zu HTTPS

## 🔍 Troubleshooting

### SSL-Zertifikat wird nicht erstellt:
1. **DNS-Records** prüfen (A-Record auf Coolify-IP)
2. **5-10 Minuten** warten nach DNS-Änderung
3. **Coolify-Logs** prüfen für SSL-Fehler
4. **Domain-Provider** prüfen (manche blockieren Let's Encrypt)

### HTTPS-Redirect funktioniert nicht:
1. **Coolify "Force HTTPS"** aktivieren
2. **Django SECURE_SSL_REDIRECT** bleibt False
3. **Cache leeren** (Browser-Cache)

### CSRF-Fehler:
1. **CSRF_TRUSTED_ORIGINS** mit https:// prüfen
2. **Alle Subdomains** hinzufügen falls nötig
3. **Browser-Cache** leeren

## 🎉 Erfolg!

### ✅ SSL funktioniert wenn:
- [ ] HTTPS-URL lädt ohne Fehler
- [ ] HTTP → HTTPS Redirect funktioniert
- [ ] SSL-Zertifikat gültig ist
- [ ] Keine Mixed Content Warnungen
- [ ] CSRF-Fehler sind weg

---

**Status:** ✅ Coolify übernimmt SSL automatisch  
**Komplexität:** 🟢 Einfach  
**Zeitaufwand:** ~5 Minuten  
**Manuelle SSL-Konfiguration:** ❌ Nicht nötig 