from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from django.http import JsonResponse

from subscriptions.models import SubscriptionPlan, UserSubscription
from .models import UserProfile

from .forms import (CustomAuthenticationForm, CustomUserCreationForm,
                    UserProfileForm, UserProfileAddressForm)


def register(request):
    """Registrierungs-View mit E-Mail-Verifikation und 14 Tage Premium-Test"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Benutzer ist inaktiv bis E-Mail verifiziert
            user.save()
            
            # UserProfile erstellen
            profile = UserProfile.objects.create(user=user)
            
            # Verifikations-E-Mail senden
            if profile.send_verification_email():
                messages.success(
                    request, 
                    "Registrierung erfolgreich! Bitte überprüfen Sie Ihre E-Mail und klicken Sie auf den Bestätigungslink, um Ihr Konto zu aktivieren."
                )
                return redirect("accounts:verification_sent")
            else:
                messages.error(
                    request, 
                    "Registrierung erfolgreich, aber es gab ein Problem beim Senden der Verifikations-E-Mail. Bitte kontaktieren Sie den Support."
                )
                return redirect("accounts:login")
        else:
            # Fehler: Status 200, aber kein Redirect
            pass
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def verification_sent(request):
    """Seite die anzeigt, dass die Verifikations-E-Mail gesendet wurde"""
    return render(request, "accounts/verification_sent.html")


def verify_email(request, token):
    """E-Mail-Verifikation durch Token"""
    try:
        profile = UserProfile.objects.get(email_verification_token=token)
        
        if profile.is_verification_token_valid():
            if profile.verify_email(token):
                # Benutzer aktivieren
                user = profile.user
                user.is_active = True
                user.save()
                
                # Premium-Test für 14 Tage erstellen
                premium_plan = SubscriptionPlan.objects.get(name="premium")
                end_date = timezone.now() + timedelta(days=14)
                UserSubscription.objects.create(
                    user=user, 
                    plan=premium_plan, 
                    is_active=True, 
                    end_date=end_date
                )
                
                # Benutzer automatisch einloggen
                login(request, user)
                
                messages.success(
                    request, 
                    "E-Mail erfolgreich bestätigt! Ihr Konto ist jetzt aktiv und Sie starten mit 14 Tagen Premium-Test. Willkommen bei MaStR Lead Generator!"
                )
                return redirect("dashboard:data")
            else:
                messages.error(request, "Ungültiger oder abgelaufener Verifikationslink.")
        else:
            messages.error(request, "Der Verifikationslink ist abgelaufen. Bitte fordern Sie einen neuen Link an.")
            
    except UserProfile.DoesNotExist:
        messages.error(request, "Ungültiger Verifikationslink.")
    
    return redirect("accounts:login")


def resend_verification(request):
    """Neue Verifikations-E-Mail senden"""
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            profile = user.profile
            
            if profile.send_verification_email():
                messages.success(
                    request, 
                    "Eine neue Verifikations-E-Mail wurde an Ihre E-Mail-Adresse gesendet."
                )
            else:
                messages.error(
                    request, 
                    "Es gab ein Problem beim Senden der E-Mail. Bitte versuchen Sie es später erneut."
                )
        except User.DoesNotExist:
            messages.error(
                request, 
                "Kein unverifiziertes Konto mit dieser E-Mail-Adresse gefunden."
            )
    
    return render(request, "accounts/resend_verification.html")


def login_view(request):
    """Angepasste Login-View mit E-Mail-Verifikations-Check"""
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(
                        request, 
                        "Ihr Konto ist noch nicht aktiviert. Bitte überprüfen Sie Ihre E-Mail und klicken Sie auf den Bestätigungslink."
                    )
                    return redirect("accounts:resend_verification")
                
                login(request, user)
                
                # Premium-Test prüfen und ggf. zurückstufen
                if hasattr(user, "subscription"):
                    user.subscription.check_and_update_trial()
                
                messages.success(request, f"Willkommen zurück, {username}!")
                return redirect("dashboard:data")
            else:
                messages.error(request, "Ungültige Anmeldedaten.")
        else:
            messages.error(request, "Bitte korrigieren Sie die Fehler unten.")
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
    """Benutzerprofil-View mit Adressfeldern"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        subscription = None

    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=request.user)
        address_form = UserProfileAddressForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and address_form.is_valid():
            user_form.save()
            address_form.save()
            messages.success(request, "Profil erfolgreich aktualisiert!")
            return redirect("accounts:profile")
    else:
        user_form = UserProfileForm(instance=request.user)
        address_form = UserProfileAddressForm(instance=request.user.profile)

    context = {
        "user": request.user, 
        "subscription": subscription, 
        "user_form": user_form,
        "address_form": address_form
    }
    return render(request, "accounts/profile.html", context)


@login_required
def complete_onboarding(request):
    """Markiert das Onboarding als abgeschlossen"""
    if request.method == "POST":
        profile = request.user.profile
        profile.onboarding_completed = True
        profile.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)
