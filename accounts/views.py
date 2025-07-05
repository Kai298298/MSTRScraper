from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import timedelta

from subscriptions.models import SubscriptionPlan, UserSubscription

from .forms import (CustomAuthenticationForm, CustomUserCreationForm,
                    UserProfileForm)


def register(request):
    """Registrierungs-View mit Datenschutz-Checkbox und 14 Tage Premium-Test"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Hole Premium- und Free-Plan
            premium_plan = SubscriptionPlan.objects.get(name="premium")
            free_plan = SubscriptionPlan.objects.get(name="free")
            # Setze Premium-Test für 14 Tage
            end_date = timezone.now() + timedelta(days=14)
            UserSubscription.objects.create(user=user, plan=premium_plan, is_active=True, end_date=end_date)
            # Logge den Benutzer automatisch ein
            login(request, user)
            messages.success(request, "Registrierung erfolgreich! Du startest mit 14 Tagen Premium-Test. Willkommen bei MaStR Analytics.")
            return redirect("dashboard:data")
        else:
            # Fehler: Status 200, aber kein Redirect
            pass
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Angepasste Login-View mit Premium-Test-Check"""
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Premium-Test prüfen und ggf. zurückstufen
                if hasattr(user, "subscription"):
                    user.subscription.check_and_update_trial()
                messages.success(request, f"Willkommen zurück, {username}!")
                return redirect("dashboard:data")
        else:
            # Fehler: Status 200, aber kein Redirect
            pass
    else:
        form = CustomAuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Logout-View: Immer Redirect nach Logout"""
    logout(request)
    messages.success(request, "Sie wurden erfolgreich abgemeldet.")
    return redirect("accounts:login")


@login_required
def profile(request):
    """Benutzerprofil-View"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        subscription = None

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil erfolgreich aktualisiert!")
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)

    context = {"user": request.user, "subscription": subscription, "form": form}
    return render(request, "accounts/profile.html", context)
