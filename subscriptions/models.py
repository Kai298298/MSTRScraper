from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """Modell für verschiedene Abonnement-Pläne"""

    PLAN_CHOICES = [
        ("free", "Kostenlos"),
        ("basic", "Basic"),
        ("premium", "Premium"),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    requests_per_day = models.IntegerField(default=10)
    max_filters = models.IntegerField(default=3)
    can_export = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Abonnement-Plan"
        verbose_name_plural = "Abonnement-Pläne"

    def __str__(self):
        return self.display_name


class UserSubscription(models.Model):
    """Modell für Benutzer-Abonnements"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_trial = models.BooleanField(default=False)  # Neue Feld für Trial-Status
    trial_end_date = models.DateTimeField(null=True, blank=True)  # Neue Feld für Trial-Ende
    requests_used_today = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Benutzer-Abonnement"
        verbose_name_plural = "Benutzer-Abonnements"

    def __str__(self):
        return f"{self.user.username} - {self.plan.display_name}"

    def start_premium_trial(self):
        """Startet eine 14-tägige Premium-Testversion"""
        premium_plan = SubscriptionPlan.objects.get(name='premium')
        self.plan = premium_plan
        self.is_trial = True
        self.trial_end_date = timezone.now() + timedelta(days=14)
        self.start_date = timezone.now()
        self.requests_used_today = 0
        self.save()
        return self

    def is_trial_active(self):
        """Prüft, ob die Trial-Version noch aktiv ist"""
        if not self.is_trial or not self.trial_end_date:
            return False
        return timezone.now() < self.trial_end_date

    def days_remaining_in_trial(self):
        """Gibt die verbleibenden Trial-Tage zurück"""
        if not self.is_trial_active():
            return 0
        remaining = self.trial_end_date - timezone.now()
        return max(0, remaining.days)

    def can_make_request(self):
        """Prüft, ob der Benutzer noch Anfragen machen kann"""
        today = timezone.now().date()

        # Reset counter if it's a new day
        if self.last_request_date != today:
            self.requests_used_today = 0
            self.last_request_date = today
            self.save()

        return self.requests_used_today < self.plan.requests_per_day

    def increment_requests(self):
        """Erhöht den Anfragen-Zähler"""
        today = timezone.now().date()

        if self.last_request_date != today:
            self.requests_used_today = 1
            self.last_request_date = today
        else:
            self.requests_used_today += 1

        self.save()

    def check_and_update_trial(self):
        """Prüft, ob das Premium-Testabo abgelaufen ist und stuft ggf. auf Free zurück."""
        if self.is_trial and self.trial_end_date and timezone.now() > self.trial_end_date:
            free_plan = SubscriptionPlan.objects.get(name="free")
            self.plan = free_plan
            self.is_trial = False
            self.trial_end_date = None
            self.end_date = None
            self.save()


class RequestLog(models.Model):
    """Log für alle Anfragen der Benutzer"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=200)
    filters_used = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Anfragen-Log"
        verbose_name_plural = "Anfragen-Logs"

    def __str__(self):
        return f"{self.user.username} - {self.endpoint} - {self.timestamp}"
