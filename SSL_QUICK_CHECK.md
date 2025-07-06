# 🔒 SSL Quick Check - Coolify Deployment

## ✅ Schnelle SSL-Einrichtung (3 Minuten)

### 1. Coolify Domain-Einstellungen
```bash
# In Coolify Dashboard:
1. Anwendung → "Domains" Tab
2. "Add Domain" → deine-domain.com
3. SSL: Let's Encrypt (automatisch)
4. "Force HTTPS": ✅ Aktiviert
5. "Save"
```

### 2. Umgebungsvariablen (KRITISCH)
```bash
# In Coolify → Environment Variables:
ALLOWED_HOSTS=deine-domain.com,www.deine-domain.com
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com
SITE_URL=https://deine-domain.com
```

### 3. DNS-Records
```bash
# Bei deinem Domain-Provider:
A-Record: @ → [Coolify Server IP]
A-Record: www → [Coolify Server IP]
# Oder CNAME: www → deine-domain.com
```

### 4. Warten und Testen
```bash
# 5-10 Minuten warten für SSL-Zertifikat
# Dann testen:
✅ https://deine-domain.com lädt
✅ http://deine-domain.com → https://deine-domain.com
✅ Grünes Schloss im Browser
✅ Keine CSRF-Fehler
```

## 🚨 Häufige SSL-Probleme

### Problem: SSL-Zertifikat wird nicht erstellt
```bash
# Lösung:
1. DNS-Records prüfen (A-Record auf Coolify-IP)
2. 10 Minuten warten
3. Coolify-Logs prüfen
```

### Problem: CSRF-Fehler bei HTTPS
```bash
# Lösung:
CSRF_TRUSTED_ORIGINS=https://deine-domain.com,https://www.deine-domain.com
```

### Problem: Mixed Content Warnungen
```bash
# Lösung:
SITE_URL=https://deine-domain.com
# Alle URLs in Templates prüfen
```

## 🎯 Erfolg-Indikatoren

### ✅ SSL funktioniert wenn:
- [ ] `https://deine-domain.com` lädt ohne Fehler
- [ ] `http://deine-domain.com` → `https://deine-domain.com` Redirect
- [ ] Grünes Schloss im Browser-Adressleiste
- [ ] Keine "Nicht sicher" Warnungen
- [ ] Admin-Interface funktioniert unter HTTPS

### ❌ SSL funktioniert NICHT wenn:
- [ ] SSL-Zertifikat "ungültig" oder "nicht vertrauenswürdig"
- [ ] CSRF-Fehler bei Formularen
- [ ] Mixed Content Warnungen im Browser
- [ ] HTTP funktioniert, HTTPS nicht

## 📞 Bei Problemen

### Coolify-Logs prüfen:
1. **Coolify Dashboard** → Deine Anwendung
2. **"Logs"** Tab
3. **SSL-Fehler** suchen

### DNS-Test:
```bash
# Terminal:
nslookup deine-domain.com
# Sollte Coolify-IP zeigen
```

### SSL-Test:
```bash
# Browser:
https://deine-domain.com
# Sollte ohne Warnungen laden
```

---

**Status:** ✅ Coolify übernimmt SSL automatisch  
**Zeitaufwand:** ~3 Minuten  
**Manuelle SSL-Konfiguration:** ❌ Nicht nötig 