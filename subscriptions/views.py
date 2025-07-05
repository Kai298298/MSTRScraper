from datetime import timedelta

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import SubscriptionPlan, RequestLog

# Stripe konfigurieren
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_your_test_key")


@login_required
def plans_view(request):
    """Zeige verfügbare Abonnement-Pläne mit optimierter UX"""
    plans = SubscriptionPlan.objects.all().order_by("price")
    current_subscription = request.user.subscription

    # Berechne Nutzungsstatistiken für bessere Conversion
    usage_percentage = 0
    if current_subscription.plan.requests_per_day > 0:
        usage_percentage = (current_subscription.requests_used_today / current_subscription.plan.requests_per_day) * 100

    # Prüfe Trial-Status
    trial_days_remaining = current_subscription.days_remaining_in_trial() if current_subscription.is_trial_active() else 0

    context = {
        "plans": plans,
        "current_subscription": current_subscription,
        "usage_percentage": usage_percentage,
        "trial_days_remaining": trial_days_remaining,
        "stripe_public_key": getattr(settings, "STRIPE_PUBLIC_KEY", "pk_test_your_test_key"),
    }
    return render(request, "subscriptions/plans.html", context)


@login_required
def start_trial(request):
    """Startet eine 14-tägige Premium-Testversion"""
    current_subscription = request.user.subscription
    
    # Prüfe, ob bereits ein Trial läuft oder abgelaufen ist
    if current_subscription.is_trial_active():
        messages.info(request, "Sie haben bereits eine aktive Premium-Testversion!")
        return redirect("subscriptions:plans")
    
    if current_subscription.is_trial and not current_subscription.is_trial_active():
        messages.warning(request, "Sie haben bereits eine Premium-Testversion genutzt. Upgrade auf Premium für alle Features!")
        return redirect("subscriptions:plans")
    
    # Starte Trial
    current_subscription.start_premium_trial()
    messages.success(request, "🎉 Ihre 14-tägige Premium-Testversion wurde gestartet! Alle Premium-Features sind jetzt verfügbar.")
    return redirect("dashboard:analytics")


@login_required
def upgrade_plan(request, plan_name):
    """Upgrade auf einen anderen Plan mit Stripe-Integration"""
    plan = get_object_or_404(SubscriptionPlan, name=plan_name)
    current_subscription = request.user.subscription

    if current_subscription.plan == plan and not current_subscription.is_trial_active():
        messages.info(request, "Sie haben bereits diesen Plan.")
        return redirect("subscriptions:plans")

    # Für Demo-Zwecke: Direkte Aktualisierung ohne Stripe
    if plan.name == "free":
        current_subscription.plan = plan
        current_subscription.start_date = timezone.now()
        current_subscription.is_trial = False
        current_subscription.trial_end_date = None
        current_subscription.requests_used_today = 0
        current_subscription.save()
        messages.success(request, f"Erfolgreich auf {plan.display_name} Plan gewechselt!")
        return redirect("subscriptions:plans")

    # Für kostenpflichtige Pläne: Stripe Checkout Session erstellen
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": plan.display_name,
                            "description": plan.description,
                        },
                        "unit_amount": int(plan.price * 100),  # Stripe erwartet Cents
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.build_absolute_uri("/subscriptions/success/"),
            cancel_url=request.build_absolute_uri("/subscriptions/plans/"),
            customer_email=request.user.email,
            metadata={
                "user_id": request.user.id,
                "plan_name": plan.name,
            },
            locale="de",
            submit_type="subscribe",
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        messages.error(request, f"Fehler beim Erstellen der Zahlungssession: {str(e)}")
        return redirect("subscriptions:plans")


@login_required
def success_view(request):
    """Erfolgreiche Zahlung - Premium-Features freischalten"""
    # In einer echten App würde hier die Stripe Webhook-Verarbeitung stehen
    # Für Demo-Zwecke aktualisieren wir direkt auf Premium
    premium_plan = SubscriptionPlan.objects.get(name="premium")
    current_subscription = request.user.subscription
    current_subscription.plan = premium_plan
    current_subscription.start_date = timezone.now()
    current_subscription.is_trial = False
    current_subscription.trial_end_date = None
    current_subscription.requests_used_today = 0
    current_subscription.save()

    messages.success(request, "🎉 Willkommen als Premium-Nutzer! Alle Features sind jetzt freigeschaltet.")
    return redirect("dashboard:analytics")


@login_required
def usage_view(request):
    """Zeige Nutzungsstatistiken mit Analytics-Integration"""
    subscription = request.user.subscription

    # Hole Nutzungsdaten der letzten 30 Tage
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_requests = RequestLog.objects.filter(user=request.user, timestamp__date__gte=thirty_days_ago).order_by(
        "-timestamp"
    )

    # Gruppiere nach Datum für Analytics
    daily_usage = {}
    for log in recent_requests:
        date = log.timestamp.date()
        if date not in daily_usage:
            daily_usage[date] = 0
        daily_usage[date] += 1

    # Berechne Statistiken
    total_requests_30_days = sum(daily_usage.values())
    avg_requests_per_day = total_requests_30_days / 30 if total_requests_30_days > 0 else 0
    usage_percentage = (subscription.requests_used_today / subscription.plan.requests_per_day) * 100

    # Trial-Informationen
    trial_days_remaining = subscription.days_remaining_in_trial() if subscription.is_trial_active() else 0

    context = {
        "subscription": subscription,
        "recent_requests": recent_requests[:50],  # Letzte 50 Anfragen
        "daily_usage": daily_usage,
        "usage_percentage": usage_percentage,
        "total_requests_30_days": total_requests_30_days,
        "avg_requests_per_day": round(avg_requests_per_day, 1),
        "days_remaining": subscription.plan.requests_per_day - subscription.requests_used_today,
        "trial_days_remaining": trial_days_remaining,
    }
    return render(request, "subscriptions/usage.html", context)


@login_required
def billing_view(request):
    """Zeige Abrechnungsinformationen"""
    subscription = request.user.subscription

    context = {
        "subscription": subscription,
    }
    return render(request, "subscriptions/billing.html", context)


@login_required
def analytics_data(request):
    """API-Endpoint für Analytics-Daten"""
    subscription = request.user.subscription

    # Hole Nutzungsdaten der letzten 30 Tage
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_requests = RequestLog.objects.filter(user=request.user, timestamp__date__gte=thirty_days_ago).order_by(
        "timestamp"
    )

    # Gruppiere nach Datum
    daily_usage = {}
    for log in recent_requests:
        date = log.timestamp.strftime("%Y-%m-%d")
        if date not in daily_usage:
            daily_usage[date] = 0
        daily_usage[date] += 1

    # Formatiere für Chart.js
    chart_data = {
        "labels": list(daily_usage.keys()),
        "datasets": [
            {
                "label": "Anfragen pro Tag",
                "data": list(daily_usage.values()),
                "borderColor": "#007bff",
                "backgroundColor": "rgba(0, 123, 255, 0.1)",
                "tension": 0.1,
            }
        ],
    }

    return JsonResponse(chart_data)
