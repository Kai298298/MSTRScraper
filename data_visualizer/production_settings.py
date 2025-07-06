"""
Produktions-Settings für MaStR Lead Generator
Diese Datei enthält sichere Einstellungen für die Produktionsumgebung
"""

import os
from pathlib import Path
from decouple import config
from .settings import *
import logging
logging.basicConfig(level=logging.INFO)
logging.info('--- START production_settings.py ---')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Produktions-Sicherheit
DEBUG = False

# Sichere SECRET_KEY (in Produktion über Umgebungsvariable setzen)
SECRET_KEY = os.environ.get('SECRET_KEY', '@*q(-up3f(d&rvc4s4it3%l04rnm@05b_^6n@3=kf4@&d-#vf2')

# Host-Konfiguration (Coolify-kompatibel)
# Akzeptiert alle Coolify-Domains automatisch
DEFAULT_ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'app.kairitter.de']
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS')
if allowed_hosts_env:
    if allowed_hosts_env.strip() == '*':
        ALLOWED_HOSTS = ['*']
    else:
        ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = DEFAULT_ALLOWED_HOSTS

logging.info(f"[DEBUG] ALLOWED_HOSTS verwendet: {ALLOWED_HOSTS}")

# CSRF-Schutz
CSRF_TRUSTED_ORIGINS = [
    "https://app.kairitter.de",
]

# SSL/HTTPS-Einstellungen (Coolify-kompatibel)
# Coolify übernimmt SSL automatisch, Django-Einstellungen sind deaktiviert
SECURE_SSL_REDIRECT = False  # Coolify übernimmt HTTPS-Redirect
SECURE_HSTS_SECONDS = 0  # Coolify übernimmt HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_FRAME_DENY = True
X_FRAME_OPTIONS = 'DENY'

# Cookie-Sicherheit (Coolify-kompatibel)
# Coolify übernimmt HTTPS, daher sind Secure-Cookies deaktiviert
SESSION_COOKIE_SECURE = False  # Coolify übernimmt HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # Coolify übernimmt HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# E-Mail-Konfiguration (flexibel für Produktion)
# Prüfe ob SMTP-Credentials verfügbar sind
email_host_user = os.environ.get('EMAIL_HOST_USER')
email_host_password = os.environ.get('EMAIL_HOST_PASSWORD')

if email_host_user and email_host_password and email_host_password != 'your-email-password':
    # Echte SMTP-Konfiguration
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = email_host_user
    EMAIL_HOST_PASSWORD = email_host_password
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', email_host_user)
    logging.info(f"📧 SMTP-E-Mail konfiguriert: {EMAIL_HOST}:{EMAIL_PORT}")
else:
    # Console-Backend für Tests
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    logging.warning("⚠️  E-Mail-Backend auf Console gesetzt - E-Mails werden nur in der Konsole angezeigt")
    logging.info("💡 Für echte E-Mails setzen Sie EMAIL_HOST_USER und EMAIL_HOST_PASSWORD in Coolify")

# Site URL für E-Mail-Verifikation
SITE_URL = os.environ.get('SITE_URL', 'http://localhost')

# Logging für Produktion
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Cache für Produktion (Redis optional)
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Fallback auf lokalen Cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Statische Dateien
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Datenbank (für Produktion PostgreSQL empfohlen)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # PostgreSQL über DATABASE_URL
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback auf SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Sicherheits-Header (angepasst für Coolify)
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = None  # Deaktiviert
SECURE_CROSS_ORIGIN_OPENER_POLICY = None  # Deaktiviert
SECURE_REFERRER_POLICY = None  # Deaktiviert

# Session-Sicherheit
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 Stunde
SESSION_SAVE_EVERY_REQUEST = True

# Rate Limiting
MAX_REQUESTS_PER_DAY = 1000
MAX_REQUESTS_PER_MINUTE = 60

# File Upload Limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True) 

logging.info("✅ Produktions-Settings geladen - DEBUG = False, SSL deaktiviert für Coolify") 