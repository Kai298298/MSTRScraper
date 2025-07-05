"""
Custom Middleware für Sicherheitsfunktionen und Rate Limiting
"""

import time
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware für Rate Limiting basierend auf IP-Adresse und Benutzer
    """

    def process_request(self, request):
        """Prüft Rate Limits vor der Verarbeitung der Anfrage"""

        # Rate Limiting nur für bestimmte Endpunkte
        rate_limit_paths = [
            '/data/',
            '/api/',
            '/anlage-speichern/',
            '/track-event/',
        ]

        if not any(request.path.startswith(path) for path in rate_limit_paths):
            return None

        # IP-Adresse ermitteln
        ip = self.get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'

        # Rate Limiting Keys
        daily_key = f"rate_limit_daily:{ip}:{user_id}"
        minute_key = f"rate_limit_minute:{ip}:{user_id}"

        # Tägliches Limit prüfen
        daily_count = cache.get(daily_key, 0)
        if daily_count >= getattr(settings, 'MAX_REQUESTS_PER_DAY', 1000):
            logger.warning(f"Daily rate limit exceeded for IP: {ip}, User: {user_id}")
            return HttpResponse("Tägliches Anfragen-Limit erreicht. Bitte versuchen Sie es morgen erneut.", status=429)

        # Minuten-Limit prüfen
        minute_count = cache.get(minute_key, 0)
        if minute_count >= getattr(settings, 'MAX_REQUESTS_PER_MINUTE', 60):
            logger.warning(f"Minute rate limit exceeded for IP: {ip}, User: {user_id}")
            return HttpResponse("Zu viele Anfragen. Bitte warten Sie eine Minute.", status=429)

        # Limits erhöhen
        cache.set(daily_key, daily_count + 1, 86400)  # 24 Stunden
        cache.set(minute_key, minute_count + 1, 60)   # 1 Minute

        return None

    def get_client_ip(self, request):
        """Ermittelt die echte IP-Adresse des Clients"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware für zusätzliche Security Headers
    """

    def process_response(self, request, response):
        """Fügt Security Headers zur Response hinzu"""

        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response['Content-Security-Policy'] = csp_policy

        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()'
        )

        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'

        # X-Frame-Options (bereits in Settings gesetzt, aber hier als Backup)
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'

        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'

        # Remove Server Header (falls möglich)
        if 'Server' in response:
            del response['Server']

        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware für detailliertes Request Logging
    """

    def process_request(self, request):
        """Loggt eingehende Anfragen"""
        request.start_time = time.time()

        # Log nur für wichtige Endpunkte
        if any(request.path.startswith(path) for path in ['/data/', '/api/', '/admin/']):
            logger.info(
                f"Request: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"User: {request.user.username if request.user.is_authenticated else 'anonymous'}"
            )

        return None

    def process_response(self, request, response):
        """Loggt ausgehende Responses"""

        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Log nur für wichtige Endpunkte und bei Fehlern
            if (any(request.path.startswith(path) for path in ['/data/', '/api/', '/admin/']) or
                response.status_code >= 400):
                logger.info(
                    f"Response: {request.method} {request.path} "
                    f"Status: {response.status_code} "
                    f"Duration: {duration:.3f}s"
                )

        return response

    def get_client_ip(self, request):
        """Ermittelt die echte IP-Adresse des Clients"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFProtectionMiddleware(MiddlewareMixin):
    """
    Erweiterte CSRF-Schutz Middleware
    """

    def process_request(self, request):
        """Zusätzliche CSRF-Validierung für kritische Endpunkte"""

        # Kritische Endpunkte, die besonderen CSRF-Schutz benötigen
        critical_endpoints = [
            '/anlage-speichern/',
            '/liste/',
            '/anlage/',
            '/admin/',
        ]

        if any(request.path.startswith(endpoint) for endpoint in critical_endpoints):
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                # Prüfe CSRF-Token
                if not hasattr(request, 'csrf_processing_done'):
                    logger.warning(f"CSRF protection bypass attempt: {request.method} {request.path}")
                    return HttpResponseForbidden("CSRF-Schutz aktiviert")

        return None


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    Middleware zur Erkennung von SQL-Injection-Versuchen
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        # SQL-Injection Patterns
        self.sql_patterns = [
            'UNION SELECT',
            'DROP TABLE',
            'DELETE FROM',
            'INSERT INTO',
            'UPDATE SET',
            'ALTER TABLE',
            'EXEC ',
            'EXECUTE ',
            '--',
            '/*',
            '*/',
            'xp_',
            'sp_',
            'WAITFOR',
            'BENCHMARK',
            'SLEEP(',
            'OR 1=1',
            'OR 1=1--',
            'OR 1=1#',
            'OR 1=1/*',
        ]

    def process_request(self, request):
        """Prüft auf SQL-Injection-Versuche"""

        # Prüfe GET-Parameter
        for key, value in request.GET.items():
            if self.contains_sql_injection(value):
                logger.warning(f"SQL Injection attempt detected in GET parameter {key}: {value}")
                return HttpResponseForbidden("Ungültige Anfrage")

        # Prüfe POST-Daten
        if request.method == 'POST':
            for key, value in request.POST.items():
                if self.contains_sql_injection(value):
                    logger.warning(f"SQL Injection attempt detected in POST parameter {key}: {value}")
                    return HttpResponseForbidden("Ungültige Anfrage")

        return None

    def contains_sql_injection(self, value):
        """Prüft ob ein Wert SQL-Injection-Patterns enthält"""
        if not isinstance(value, str):
            return False

        value_upper = value.upper()
        return any(pattern.upper() in value_upper for pattern in self.sql_patterns)
