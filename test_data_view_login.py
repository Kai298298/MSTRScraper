#!/usr/bin/env python3
"""
Testet die /data/-Seite als eingeloggter Nutzer und prüft, ob Suchergebnisse angezeigt werden.
"""
import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8000"
LOGIN_URL = BASE_URL + "/accounts/login/"
DATA_URL = BASE_URL + "/data/"
USERNAME = "testuser"
PASSWORD = "testpass123"

def extract_csrf_token(html):
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return match.group(1) if match else None

def main():
    session = requests.Session()
    # Login-Seite holen (CSRF)
    resp = session.get(LOGIN_URL)
    csrf = extract_csrf_token(resp.text)
    if not csrf:
        print("❌ Kein CSRF-Token gefunden!")
        return
    # Login durchführen
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "csrfmiddlewaretoken": csrf,
    }
    headers = {"Referer": LOGIN_URL}
    resp = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
    if "Abmelden" not in resp.text and "Logout" not in resp.text:
        print("❌ Login fehlgeschlagen!")
        return
    print("✅ Login erfolgreich!")
    # /data/ abrufen
    resp = session.get(DATA_URL)
    print("--- HTML-Ausschnitt /data/ ---")
    print(resp.text[:500])
    # Prüfen auf typische Tabellenelemente
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if table and hasattr(table, 'find_all'):
        rows = table.find_all("tr")
        print(f"✅ Tabelle gefunden, Zeilen: {len(rows)}")
        if len(rows) > 1:
            print("✅ Suchergebnisse werden angezeigt!")
        else:
            print("⚠️  Tabelle gefunden, aber keine Datenzeilen!")
    else:
        print("❌ Keine Tabelle/Suchergebnisse gefunden!")

if __name__ == "__main__":
    main() 