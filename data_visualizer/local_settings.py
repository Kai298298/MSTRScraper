"""
Lokale Entwicklungssettings für MaStR Lead Generator
Diese Datei enthält Einstellungen für die lokale Entwicklung
"""

from .production_settings import *

# Debug für lokale Entwicklung aktivieren
DEBUG = True

# Lokale Hosts erlauben
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CSRF für lokale Entwicklung
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# SSL/HTTPS-Einstellungen für lokale Entwicklung deaktivieren
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_FRAME_DENY = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Cookie-Sicherheit für lokale Entwicklung lockern
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# E-Mail für lokale Entwicklung auf Console-Backend setzen
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Site URL für lokale Entwicklung
SITE_URL = 'http://localhost:8000'

print("✅ Lokale Entwicklungssettings geladen - DEBUG = True") 