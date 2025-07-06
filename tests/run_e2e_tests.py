#!/usr/bin/env python3
"""
E2E-Test Runner für MSTRScraper
Führt automatisch Tests aus und erstellt Test-Accounts
"""

import os
import sys
import subprocess
import asyncio
import time
from pathlib import Path

# Django-Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_visualizer.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from subscriptions.models import SubscriptionPlan, UserSubscription
from accounts.models import UserProfile
from django.utils import timezone
from datetime import timedelta


def create_test_accounts():
    """Erstellt Test-Accounts für E2E-Tests"""
    print("🧪 Erstelle Test-Accounts für E2E-Tests...")
    
    # Test-Accounts definieren
    test_accounts = [
        {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    for account_data in test_accounts:
        username = account_data['username']
        
        # Prüfe ob Account bereits existiert
        if User.objects.filter(username=username).exists():
            print(f"⚠️ Account '{username}' existiert bereits")
            continue
        
        try:
            # Erstelle neuen User
            user = User.objects.create_user(
                username=username,
                email=account_data['email'],
                password=account_data['password'],
                first_name=account_data['first_name'],
                last_name=account_data['last_name'],
                is_staff=account_data['is_staff'],
                is_superuser=account_data['is_superuser'],
                is_active=True
            )
            
            # UserProfile wird automatisch durch Signal erstellt
            profile = user.profile
            profile.email_verified = True
            profile.onboarding_completed = True
            profile.save()
            
            # Premium-Subscription für Test-User erstellen
            if username == 'testuser':
                try:
                    premium_plan = SubscriptionPlan.objects.get(name='premium')
                    end_date = timezone.now() + timedelta(days=30)  # 30 Tage Test
                    UserSubscription.objects.create(
                        user=user,
                        plan=premium_plan,
                        is_active=True,
                        end_date=end_date
                    )
                    print(f"✅ Premium-Subscription für '{username}' erstellt")
                except SubscriptionPlan.DoesNotExist:
                    print(f"⚠️ Premium-Plan nicht gefunden für '{username}'")
            
            print(f"✅ Test-Account '{username}' erfolgreich erstellt")
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen von '{username}': {str(e)}")
    
    print("\n📋 Test-Accounts Übersicht:")
    print("=" * 50)
    print("👤 testuser / testpass123 (Premium-Test)")
    print("🔑 admin / adminpass123 (Administrator)")
    print("\n💡 Diese Accounts können für E2E-Tests verwendet werden")


def start_django_server():
    """Startet Django-Server im Hintergrund"""
    print("🚀 Starte Django-Server...")
    
    # Server im Hintergrund starten
    server_process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver', '8000', '--noreload'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Warte kurz bis Server gestartet ist
    time.sleep(3)
    
    return server_process


def run_e2e_tests():
    """Führt E2E-Tests aus"""
    print("🧪 Führe E2E-Tests aus...")
    
    # Importiere und führe Tests aus
    from tests.e2e_test_app import E2ETestApp
    
    async def run_tests():
        tester = E2ETestApp("http://localhost:8000")
        await tester.run_tests()
    
    # Tests asynchron ausführen
    asyncio.run(run_tests())


def main():
    """Hauptfunktion"""
    print("🧪 MSTRScraper E2E-Test Runner")
    print("=" * 50)
    
    try:
        # 1. Test-Accounts erstellen
        create_test_accounts()
        
        # 2. Django-Server starten
        server_process = start_django_server()
        
        try:
            # 3. E2E-Tests ausführen
            run_e2e_tests()
            
        finally:
            # 4. Server beenden
            print("🛑 Beende Django-Server...")
            server_process.terminate()
            server_process.wait()
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests durch Benutzer abgebrochen")
    except Exception as e:
        print(f"❌ Fehler beim Ausführen der Tests: {str(e)}")
    
    print("\n✅ E2E-Test Runner beendet")


if __name__ == "__main__":
    main() 