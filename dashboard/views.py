import csv
import json
import math
import os
import sqlite3

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count


from subscriptions.models import RequestLog, SubscriptionPlan, UserSubscription
from dashboard.models import AnlagenListe, GespeicherteAnlage, AnlagenFeedback

# API ViewSets
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import GespeicherteAnlageSerializer, AnlagenListeSerializer, UserSerializer


def get_db_connection():
    """
    Erstellt eine Verbindung zur externen MaStR-Datenbank
    
    Diese Funktion wird für direkte SQLite-Zugriffe verwendet,
    wenn Django's ORM nicht ausreicht.
    
    Returns:
        sqlite3.Connection: Verbindung zur data.sqlite Datenbank
    """
    data_db_path = os.path.join(settings.BASE_DIR, "data", "data.sqlite")
    return sqlite3.connect(data_db_path)


def load_plz_coordinates():
    """
    Lädt PLZ-Koordinaten aus der CSV-Datei
    
    Diese Funktion liest die PLZ-Koordinaten-Datei ein und erstellt
    ein Dictionary für schnelle Koordinaten-Lookups.
    
    Returns:
        dict: Dictionary mit PLZ als Schlüssel und (lat, lon) als Werte
    """
    coordinates = {}
    csv_path = os.path.join(settings.BASE_DIR, "data", "plz_coordinates.csv")
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                plz = row.get('plz', '').strip()
                if plz and row.get('lat') and row.get('lon'):
                    try:
                        coordinates[plz] = (float(row['lat']), float(row['lon']))
                    except ValueError:
                        continue
    
    return coordinates


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Berechnet die Entfernung zwischen zwei Koordinaten (Haversine-Formel)
    
    Die Haversine-Formel berechnet die kürzeste Entfernung zwischen zwei
    Punkten auf einer Kugel (Erde) über die Oberfläche.
    
    Args:
        lat1 (float): Breitengrad des ersten Punktes
        lon1 (float): Längengrad des ersten Punktes
        lat2 (float): Breitengrad des zweiten Punktes
        lon2 (float): Längengrad des zweiten Punktes
        
    Returns:
        float: Entfernung in Kilometern
    """
    # Umrechnung in Radiant
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Differenzen
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine-Formel
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Erdradius in Kilometern
    r = 6371
    
    return c * r


def get_coordinates_for_plz(plz):
    """
    Holt Koordinaten für eine PLZ aus dem geladenen Dictionary
    
    Args:
        plz (str): Postleitzahl
        
    Returns:
        tuple: (lat, lon) Koordinaten oder None wenn nicht gefunden
    """
    return PLZ_COORDINATES.get(str(plz))


def get_user_subscription(user):
    """
    Holt die aktuelle Abonnement-Informationen eines Benutzers
    
    Prüft, ob der Benutzer ein aktives Premium-Abonnement hat
    und gibt die entsprechenden Informationen zurück.
    
    Args:
        user: Django User-Objekt
        
    Returns:
        dict: Abonnement-Informationen oder None
    """
    try:
        subscription = UserSubscription.objects.get(user=user)
        return {
            'is_premium': subscription.is_active and subscription.plan.is_premium,
            'plan_name': subscription.plan.name,
            'expires_at': subscription.expires_at,
            'requests_used': subscription.requests_used,
            'requests_limit': subscription.plan.request_limit
        }
    except UserSubscription.DoesNotExist:
        # Fallback auf kostenlosen Plan
        try:
            free_plan = SubscriptionPlan.objects.get(name="Kostenlos")
            return {
                'is_premium': False,
                'plan_name': free_plan.name,
                'expires_at': None,
                'requests_used': 0,
                'requests_limit': free_plan.request_limit
            }
        except SubscriptionPlan.DoesNotExist:
            return None


def log_request(user, endpoint, filters_used, success=True, error_message=""):
    """
    Protokolliert API-Anfragen für Analytics und Monitoring
    
    Speichert Informationen über jede Anfrage in der Datenbank
    für spätere Analyse und Monitoring.
    
    Args:
        user: Django User-Objekt
        endpoint (str): Aufgerufener Endpunkt
        filters_used (dict): Verwendete Filter
        success (bool): Ob die Anfrage erfolgreich war
        error_message (str): Fehlermeldung bei Misserfolg
    """
    try:
        RequestLog.objects.create(
            user=user,
            endpoint=endpoint,
            filters_used=json.dumps(filters_used),
            success=success,
            error_message=error_message,
            timestamp=timezone.now()
        )
    except Exception as e:
        # Logging-Fehler sollten die Hauptfunktionalität nicht beeinträchtigen
        print(f"Fehler beim Logging: {e}")


def check_export_permission(user):
    """
    Prüft, ob ein Benutzer Export-Funktionen nutzen darf
    
    Args:
        user: Django User-Objekt
        
    Returns:
        bool: True wenn Export erlaubt ist
    """
    subscription = get_user_subscription(user)
    return subscription and subscription.get('is_premium', False)


def check_request_limit(user):
    """
    Prüft, ob ein Benutzer noch Anfragen übrig hat
    
    Args:
        user: Django User-Objekt
        
    Returns:
        bool: True wenn noch Anfragen verfügbar sind
    """
    subscription = get_user_subscription(user)
    if not subscription:
        return False
    
    return subscription.get('requests_used', 0) < subscription.get('requests_limit', 0)


def increment_request_count(user):
    """
    Erhöht den Anfragen-Zähler eines Benutzers
    
    Args:
        user: Django User-Objekt
    """
    try:
        subscription = UserSubscription.objects.get(user=user)
        subscription.requests_used += 1
        subscription.save()
    except UserSubscription.DoesNotExist:
        pass  # Kein Abonnement = kein Zähler


def check_premium_feature(user):
    """
    Prüft, ob ein Benutzer Premium-Features nutzen darf
    
    Args:
        user: Django User-Objekt
        
    Returns:
        bool: True wenn Premium-Features verfügbar sind
    """
    subscription = get_user_subscription(user)
    return subscription and subscription.get('is_premium', False)


@login_required
def data_view(request):
    """
    Hauptview für die Lead-Suche im Marktstammdatenregister.
    Zeigt gefilterte Ergebnisse aus der MaStR-Datenbank an.
    """
    # Prüfen ob CSV-Export gewünscht ist
    if request.GET.get("export") == "csv":
        if not check_export_permission(request.user):
            messages.error(request, "CSV-Export ist nur im Premium-Tarif verfügbar.")
            return redirect("dashboard:data")
        return export_csv(request, **get_filter_params(request))

    # Prüfen ob Benutzer noch Anfragen machen kann
    if not check_request_limit(request.user):
        messages.error(request, "Sie haben Ihr tägliches Anfragen-Limit erreicht. Bitte upgraden Sie Ihren Tarif.")
        return render(request, "dashboard/data.html", get_empty_context())

    # Filter-Parameter aus der URL auslesen
    filter_params = get_filter_params(request)

    # Prüfen ob zu viele Filter verwendet werden
    subscription = get_user_subscription(request.user)
    active_filters = sum(1 for value in filter_params.values() if value)
    if active_filters > subscription.plan.max_filters:
        messages.error(
            request,
            f"Sie können maximal {subscription.plan.max_filters} Filter gleichzeitig verwenden. Bitte reduzieren Sie die Anzahl der Filter.",
        )
        return render(request, "dashboard/data.html", get_empty_context())

    try:
        # Anfragen-Zähler erhöhen
        increment_request_count(request.user)

        # Anfrage loggen
        log_request(request.user, "data_view", filter_params)

        # SQL-Query dynamisch aufbauen basierend auf den Filtern
        query = "SELECT * FROM test_Tabelle1 WHERE 1=1"
        params = []

        # Freitextsuche
        if filter_params["freitext"]:
            freitext = filter_params["freitext"]
            freitext_conditions = [
                "`Anzeige-Name der Einheit` LIKE ?",
                "`Energieträger` LIKE ?",
                "`Bundesland` LIKE ?",
                "`Ort` LIKE ?",
                "`Postleitzahl` LIKE ?",
                "`Name des Anlagenbetreibers (nur Org.)` LIKE ?",
                "`Technologie der Stromerzeugung` LIKE ?",
                "`Art der Solaranlage` LIKE ?",
                "`Betriebs-Status` LIKE ?",
            ]
            freitext_params = [f"%{freitext}%" for _ in freitext_conditions]
            query += " AND (" + " OR ".join(freitext_conditions) + ")"
            params.extend(freitext_params)

        # Spezifische Filter-Bedingungen hinzufügen
        if filter_params["energietraeger"]:
            query += " AND `Energieträger` = ?"
            params.append(filter_params["energietraeger"])
        if filter_params["bundesland"]:
            query += " AND `Bundesland` = ?"
            params.append(filter_params["bundesland"])
        if filter_params["leistung_min"]:
            query += " AND CAST(`Bruttoleistung der Einheit` AS REAL) >= ?"
            params.append(filter_params["leistung_min"])
        if filter_params["leistung_max"]:
            query += " AND CAST(`Bruttoleistung der Einheit` AS REAL) <= ?"
            params.append(filter_params["leistung_max"])
        if filter_params["status"]:
            query += " AND `Betriebs-Status` = ?"
            params.append(filter_params["status"])
        if filter_params["ort"]:
            query += " AND `Ort` LIKE ?"
            params.append(f"%{filter_params['ort']}%")
        if filter_params["plz"]:
            query += " AND `Postleitzahl` LIKE ?"
            params.append(f"%{filter_params['plz']}%")
        if filter_params["technologie"]:
            query += " AND `Technologie der Stromerzeugung` = ?"
            params.append(filter_params["technologie"])
        if filter_params["art_solar"]:
            query += " AND `Art der Solaranlage` = ?"
            params.append(filter_params["art_solar"])
        if filter_params["betreiber"]:
            query += " AND `Name des Anlagenbetreibers (nur Org.)` LIKE ?"
            params.append(f"%{filter_params['betreiber']}%")
        if filter_params["datum_von"]:
            query += " AND date(`Inbetriebnahmedatum der Einheit`) >= date(?)"
            params.append(filter_params["datum_von"])
        if filter_params["datum_bis"]:
            query += " AND date(`Inbetriebnahmedatum der Einheit`) <= date(?)"
            params.append(filter_params["datum_bis"])

        # DEBUG: Query und Filter ausgeben
        print("[DEBUG] SQL-Query:", query)
        print("[DEBUG] Query-Parameter:", params)
        print("[DEBUG] Filter-Parameter:", filter_params)

        # Für Filter-Dropdowns: Alle verfügbaren Werte aus der Datenbank holen
        with get_db_connection() as conn:
            c = conn.cursor()

            # Energieträger-Liste
            c.execute(
                "SELECT DISTINCT `Energieträger` FROM test_Tabelle1 WHERE `Energieträger` IS NOT NULL AND `Energieträger` != '' ORDER BY `Energieträger`"
            )
            energietraeger_list = [row[0] for row in c.fetchall()]

            # Bundesland-Liste
            c.execute(
                "SELECT DISTINCT `Bundesland` FROM test_Tabelle1 WHERE `Bundesland` IS NOT NULL AND `Bundesland` != '' ORDER BY `Bundesland`"
            )
            bundesland_list = [row[0] for row in c.fetchall()]

            # Status-Liste
            c.execute(
                "SELECT DISTINCT `Betriebs-Status` FROM test_Tabelle1 WHERE `Betriebs-Status` IS NOT NULL AND `Betriebs-Status` != '' ORDER BY `Betriebs-Status`"
            )
            status_list = [row[0] for row in c.fetchall()]

            # Technologie-Liste
            c.execute(
                "SELECT DISTINCT `Technologie der Stromerzeugung` FROM test_Tabelle1 WHERE `Technologie der Stromerzeugung` IS NOT NULL AND `Technologie der Stromerzeugung` != '' ORDER BY `Technologie der Stromerzeugung`"
            )
            technologie_list = [row[0] for row in c.fetchall()]

            # Solaranlagen-Art-Liste
            c.execute(
                "SELECT DISTINCT `Art der Solaranlage` FROM test_Tabelle1 WHERE `Art der Solaranlage` IS NOT NULL AND `Art der Solaranlage` != '' ORDER BY `Art der Solaranlage`"
            )
            art_solar_list = [row[0] for row in c.fetchall()]

            # Gefilterte Daten holen
            c.execute(query, params)
            rows = c.fetchall()
            columns = [desc[0] for desc in c.description]

            # Spaltennamen übersetzen
            columns = translate_column_names(columns)

        # Umkreissuche anwenden, falls angegeben
        if filter_params["radius_plz"] and filter_params["radius_km"]:
            target_coords = get_coordinates_for_plz(filter_params["radius_plz"])
            if target_coords:
                filtered_rows = []
                radius_km = float(filter_params["radius_km"])

                for row in rows:
                    # Koordinaten aus der Datenbank extrahieren (Spalten 18 und 19)
                    try:
                        lat_str = row[18]  # Koordinate: Breitengrad (WGS84)
                        lon_str = row[19]  # Koordinate: Längengrad (WGS84)

                        if lat_str and lon_str and lat_str.strip() and lon_str.strip():
                            lat = float(lat_str)
                            lon = float(lon_str)

                            # Distanz berechnen
                            distance = haversine_distance(target_coords["lat"], target_coords["lon"], lat, lon)

                            # Nur Einträge im Radius hinzufügen
                            if distance <= radius_km:
                                # Distanz zur Zeile hinzufügen
                                row_with_distance = list(row) + [f"{distance:.1f} km"]
                                filtered_rows.append(row_with_distance)
                    except (ValueError, IndexError):
                        # Wenn Koordinaten nicht verfügbar oder ungültig, überspringen
                        continue

                rows = filtered_rows
                # Spalten erweitern um Distanz
                columns = columns + ["Distanz"]
            else:
                messages.warning(
                    request,
                    f'PLZ {filter_params["radius_plz"]} nicht in der Koordinaten-Tabelle gefunden. Umkreissuche wird ignoriert.',
                )

        # Paginierung für die Anzeige
        page_number = int(request.GET.get("page", 1))
        page_size = 100  # Erhöht von 30 auf 100 für bessere Kartenansicht
        start = (page_number - 1) * page_size
        end = start + page_size
        page_rows = rows[start:end]
        paginator = Paginator(rows, page_size)
        page_obj = paginator.get_page(page_number)

        # Anlagen-Listen für Premium-User
        anlagen_listen = []
        if check_premium_feature(request.user):
            anlagen_listen = AnlagenListe.objects.filter(user=request.user).order_by("-erstellt_am")

        # Context für das Template
        context = {
            "columns": columns,
            "rows": page_rows,
            "page_obj": page_obj,
            "energietraeger_list": energietraeger_list,
            "bundesland_list": bundesland_list,
            "status_list": status_list,
            "technologie_list": technologie_list,
            "art_solar_list": art_solar_list,
            "filter": filter_params,
            "subscription": subscription,
            "can_export": subscription.plan.can_export,
            "requests_remaining": subscription.plan.requests_per_day - subscription.requests_used_today,
            "max_filters": subscription.plan.max_filters,
            "anlagen_listen": anlagen_listen,
            "can_save_lists": check_premium_feature(request.user),
        }

        # Anlagen-Daten für Karte vorbereiten (ALLE gefilterten Anlagen, nicht nur die der aktuellen Seite)
        anlagen_liste = []
        for a in rows:  # Verwende alle gefilterten Anlagen statt nur page_rows
            try:
                # Zuerst prüfen, ob präzise Koordinaten vorhanden sind
                lat = None
                lon = None
                has_precise_coords = False
                
                if a[18] and a[19] and str(a[18]).strip() and str(a[19]).strip():
                    try:
                        lat = float(a[18])
                        lon = float(a[19])
                        has_precise_coords = True
                    except (ValueError, TypeError):
                        pass
                
                # Nur wenn keine präzisen Koordinaten vorhanden sind, PLZ-Koordinaten verwenden
                if not has_precise_coords and a[9]:  # PLZ in Spalte 9
                    coords = get_coordinates_for_plz(str(a[9]))
                    if coords:
                        lat = coords["lat"]
                        lon = coords["lon"]
                
                if lat and lon:
                    anlagen_liste.append({
                        "lat": lat,
                        "lon": lon,
                        "name": a[1] if a[1] else "Unbekannte Anlage",  # Anzeige-Name der Einheit in Spalte 1
                        "ort": a[10] if a[10] else "",  # Ort in Spalte 10
                        "plz": a[9] if a[9] else "",  # Postleitzahl in Spalte 9
                        "energietraeger": a[3] if a[3] else "",  # Energieträger in Spalte 3
                        "leistung": a[4] if a[4] else "",  # Bruttoleistung in Spalte 4
                        "strasse": a[11] if a[11] else "",  # Straße in Spalte 11
                        "hausnummer": a[12] if a[12] else "",  # Hausnummer in Spalte 12
                        "has_precise_coords": has_precise_coords,  # Flag für präzise Koordinaten
                    })
            except (ValueError, IndexError, TypeError):
                # Bei Fehlern überspringen
                continue
                
        context["anlagen_liste"] = json.dumps(anlagen_liste)
        return render(request, "dashboard/data.html", context)

    except sqlite3.OperationalError as e:
        # Fallback wenn MaStR-Datenbank nicht verfügbar ist
        log_request(request.user, "data_view", filter_params, success=False, error_message=str(e))
        context = get_empty_context()
        context["error"] = (
            f"Datenbankfehler: {str(e)}. Bitte stellen Sie sicher, dass die MaStR-Datenbank verfügbar ist."
        )
        return render(request, "dashboard/data.html", context)


def build_sql_filter(query, params, filter_params):
    # Freitextsuche
    if filter_params["freitext"]:
        freitext = filter_params["freitext"]
        freitext_conditions = [
            "`Anzeige-Name der Einheit` LIKE ?",
            "`Energieträger` LIKE ?",
            "`Bundesland` LIKE ?",
            "`Ort` LIKE ?",
            "`Postleitzahl` LIKE ?",
            "`Name des Anlagenbetreibers (nur Org.)` LIKE ?",
            "`Technologie der Stromerzeugung` LIKE ?",
            "`Art der Solaranlage` LIKE ?",
            "`Betriebs-Status` LIKE ?",
        ]
        freitext_params = [f"%{freitext}%" for _ in freitext_conditions]
        query += " AND (" + " OR ".join(freitext_conditions) + ")"
        params.extend(freitext_params)
    # Weitere Filter
    if filter_params["energietraeger"]:
        query += " AND `Energieträger` = ?"
        params.append(filter_params["energietraeger"])
    if filter_params["bundesland"]:
        query += " AND `Bundesland` = ?"
        params.append(filter_params["bundesland"])
    if filter_params["leistung_min"]:
        query += " AND CAST(`Bruttoleistung der Einheit` AS REAL) >= ?"
        params.append(filter_params["leistung_min"])
    if filter_params["leistung_max"]:
        query += " AND CAST(`Bruttoleistung der Einheit` AS REAL) <= ?"
        params.append(filter_params["leistung_max"])
    if filter_params["status"]:
        query += " AND `Betriebs-Status` = ?"
        params.append(filter_params["status"])
    if filter_params["ort"]:
        query += " AND `Ort` LIKE ?"
        params.append(f"%{filter_params['ort']}%")
    if filter_params["plz"]:
        query += " AND `Postleitzahl` LIKE ?"
        params.append(f"%{filter_params['plz']}%")
    if filter_params["technologie"]:
        query += " AND `Technologie der Stromerzeugung` = ?"
        params.append(filter_params["technologie"])
    if filter_params["art_solar"]:
        query += " AND `Art der Solaranlage` = ?"
        params.append(filter_params["art_solar"])
    if filter_params["betreiber"]:
        query += " AND `Name des Anlagenbetreibers (nur Org.)` LIKE ?"
        params.append(f"%{filter_params['betreiber']}%")
    if filter_params["datum_von"]:
        query += " AND date(`Inbetriebnahmedatum der Einheit`) >= date(?)"
        params.append(filter_params["datum_von"])
    if filter_params["datum_bis"]:
        query += " AND date(`Inbetriebnahmedatum der Einheit`) <= date(?)"
        params.append(filter_params["datum_bis"])
    return query, params


@login_required
def anlagen_listen_view(request):
    """Hauptansicht für Anlagenlisten mit Filterung"""
    if request.method == "POST":
        listenname = request.POST.get("listenname")
        beschreibung = request.POST.get("beschreibung", "")

        if listenname:
            AnlagenListe.objects.create(user=request.user, name=listenname, beschreibung=beschreibung)
            messages.success(request, f'Liste "{listenname}" erfolgreich erstellt!')
            return redirect("dashboard:anlagen_listen")
        else:
            # Fehler: kein Listenname, kein Redirect
            return render(request, "dashboard/anlagen_listen.html", {"listen": []}, status=400)

    listen = (
        AnlagenListe.objects.filter(user=request.user)
        .annotate(anzahl_anlagen=Count("anlagen"))
        .order_by("-aktualisiert_am")
    )

    return render(request, "dashboard/anlagen_listen.html", {"listen": listen})


@login_required
def liste_detail_view(request, liste_id):
    """Detailansicht einer Anlagenliste"""
    try:
        liste = AnlagenListe.objects.get(id=liste_id, user=request.user)
    except AnlagenListe.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        action = request.POST.get("action")
        anlage_id = request.POST.get("anlage_id")

        if action == "notiz" and anlage_id:
            anlage = get_object_or_404(GespeicherteAnlage, id=anlage_id, liste=liste)
            anlage.notizen = request.POST.get("notizen", "")
            anlage.save()
            messages.success(request, "Notiz gespeichert!")

        elif action == "entfernen" and anlage_id:
            anlage = get_object_or_404(GespeicherteAnlage, id=anlage_id, liste=liste)
            anlage.delete()
            messages.success(request, "Anlage aus Liste entfernt!")

        elif action == "feedback" and anlage_id:
            feedback_typ = request.POST.get("feedback_typ")
            beschreibung = request.POST.get("feedback_beschreibung", "").strip()
            if feedback_typ and beschreibung:
                AnlagenFeedback.objects.create(
                    gespeicherte_anlage=anlage,
                    user=request.user,
                    feedback_typ=feedback_typ,
                    titel=f"Feedback zu {anlage.anlagenname}",
                    beschreibung=beschreibung,
                )
                messages.success(request, "Vielen Dank für Ihr Feedback!")
            else:
                messages.error(request, "Bitte wählen Sie einen Feedback-Typ und geben Sie eine Beschreibung an.")

    anlagen = liste.anlagen.all()

    # Koordinaten für Karte vorbereiten
    anlagen_json = []
    plz_coords = load_plz_coordinates()

    for anlage in anlagen:
        lat = None
        lon = None

        # Versuche Koordinaten aus PLZ zu holen
        if anlage.plz:
            coords = get_coordinates_for_plz(anlage.plz)
            if coords:
                lat = coords["lat"]
                lon = coords["lon"]

        if lat and lon:
            anlagen_json.append(
                {
                    "name": anlage.anlagenname or "Unbekannt",
                    "ort": anlage.ort or "",
                    "plz": anlage.plz or "",
                    "energietraeger": anlage.energietraeger or "",
                    "leistung": anlage.leistung or "",
                    "lat": lat,
                    "lon": lon,
                }
            )

    # Pagination
    paginator = Paginator(anlagen, 20)
    page = request.GET.get("page")
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(
        request,
        "dashboard/liste_detail.html",
        {"liste": liste, "anlagen": page_obj, "page_obj": page_obj, "anlagen_json": json.dumps(anlagen_json)},
    )


@login_required
def liste_loeschen(request, liste_id):
    """Löscht eine Anlagenliste"""
    try:
        liste = AnlagenListe.objects.get(id=liste_id, user=request.user)
    except AnlagenListe.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        listenname = liste.name
        liste.delete()
        messages.success(request, f'Liste "{listenname}" erfolgreich gelöscht!')
        return redirect("dashboard:anlagen_listen")

    return render(request, "dashboard/liste_loeschen_confirm.html", {"liste": liste})


@login_required
def liste_duplizieren(request, liste_id):
    """Dupliziert eine Anlagenliste"""
    try:
        original_liste = AnlagenListe.objects.get(id=liste_id, user=request.user)
    except AnlagenListe.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        neuer_name = request.POST.get("neuer_name")
        if neuer_name:
            # Neue Liste erstellen
            neue_liste = AnlagenListe.objects.create(
                user=request.user, name=neuer_name, beschreibung=f"Kopie von: {original_liste.beschreibung}"
            )

            # Anlagen kopieren
            for anlage in original_liste.anlagen.all():
                GespeicherteAnlage.objects.create(
                    liste=neue_liste,
                    anlagen_id=anlage.anlagen_id,
                    anlagenname=anlage.anlagenname,
                    energietraeger=anlage.energietraeger,
                    leistung=anlage.leistung,
                    bundesland=anlage.bundesland,
                    ort=anlage.ort,
                    plz=anlage.plz,
                    status=anlage.status,
                    technologie=anlage.technologie,
                    betreiber=anlage.betreiber,
                    inbetriebnahme=anlage.inbetriebnahme,
                    notizen=anlage.notizen,
                )

            messages.success(request, f'Liste "{neuer_name}" erfolgreich erstellt!')
            return redirect("dashboard:liste_detail", liste_id=neue_liste.id)

    return render(request, "dashboard/liste_duplizieren.html", {"liste": original_liste})


@csrf_exempt
@login_required
@require_POST
def anlage_speichern(request):
    """Speichert eine oder mehrere Anlagen in einer Liste für den Nutzer"""
    try:
        data = json.loads(request.body.decode("utf-8"))

        # Prüfe ob es sich um mehrere Anlagen handelt (neue Checkbox-Funktionalität)
        if "anlagen" in data:
            return save_multiple_anlagen(request, data)
        else:
            # Alte Funktionalität für einzelne Anlagen (aus Kartenansicht)
            return save_single_anlage(request, data)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def save_single_anlage(request, data):
    """Speichert eine einzelne Anlage (alte Funktionalität)"""
    anlage = data.get("anlage")
    notizen = data.get("notizen", "")
    listenname = data.get("listenname")
    beschreibung = data.get("beschreibung", "")
    liste_id = data.get("liste_id")

    # Entweder neue Liste oder bestehende
    if liste_id:
        liste = AnlagenListe.objects.get(id=liste_id, user=request.user)
    else:
        if not listenname:
            return JsonResponse({"success": False, "error": "Listenname fehlt."})
        liste, created = AnlagenListe.objects.get_or_create(
            user=request.user, name=listenname, defaults={"beschreibung": beschreibung}
        )

    # Gespeicherte Anlage anlegen
    gespeicherte, created = GespeicherteAnlage.objects.get_or_create(
        liste=liste,
        anlagen_id=anlage.get("anlagen_id"),
        defaults={
            "anlagenname": anlage.get("anlagenname", ""),
            "energietraeger": anlage.get("energietraeger", ""),
            "leistung": anlage.get("leistung") or None,
            "bundesland": anlage.get("bundesland", ""),
            "ort": anlage.get("ort", ""),
            "plz": anlage.get("plz", ""),
            "status": anlage.get("status", ""),
            "technologie": anlage.get("technologie", ""),
            "betreiber": anlage.get("betreiber", ""),
            "inbetriebnahme": parse_date(anlage.get("inbetriebnahme")) if anlage.get("inbetriebnahme") else None,
            "notizen": notizen,
        },
    )

    if not created:
        return JsonResponse({"success": False, "error": "Anlage ist bereits in dieser Liste gespeichert."})

    return JsonResponse({"success": True})


def save_multiple_anlagen(request, data):
    """Speichert mehrere Anlagen gleichzeitig (neue Checkbox-Funktionalität)"""
    anlagen = data.get("anlagen", [])
    liste_id = data.get("liste_id")
    neue_liste_name = data.get("neue_liste_name", "").strip()
    neue_liste_beschreibung = data.get("neue_liste_beschreibung", "").strip()
    notizen = data.get("notizen", "").strip()

    if not anlagen:
        return JsonResponse({"success": False, "error": "Keine Anlagen ausgewählt."})

    # Liste bestimmen
    if liste_id:
        try:
            liste = AnlagenListe.objects.get(id=liste_id, user=request.user)
        except AnlagenListe.DoesNotExist:
            return JsonResponse({"success": False, "error": "Liste nicht gefunden."})
    else:
        if not neue_liste_name:
            return JsonResponse({"success": False, "error": "Name für neue Liste fehlt."})

        liste, created = AnlagenListe.objects.get_or_create(
            user=request.user, name=neue_liste_name, defaults={"beschreibung": neue_liste_beschreibung}
        )

    # Anlagen speichern
    saved_count = 0
    already_exists_count = 0

    for anlage_data in anlagen:
        try:
            # Extrahiere Anlagendaten aus der Tabellenzeile
            anlagen_id = anlage_data.get("anlagen_id", "")
            anlagenname = anlage_data.get("anlagenname", "")
            energietraeger = anlage_data.get("energietraeger", "")
            leistung = anlage_data.get("leistung", "")
            bundesland = anlage_data.get("bundesland", "")
            ort = anlage_data.get("ort", "")
            plz = anlage_data.get("plz", "")
            status = anlage_data.get("status", "")
            technologie = anlage_data.get("technologie", "")
            betreiber = anlage_data.get("betreiber", "")
            inbetriebnahme = anlage_data.get("inbetriebnahme", "")

            # Versuche Leistung zu parsen
            try:
                leistung_parsed = float(leistung) if leistung else None
            except (ValueError, TypeError):
                leistung_parsed = None

            # Versuche Datum zu parsen
            try:
                inbetriebnahme_parsed = parse_date(inbetriebnahme) if inbetriebnahme else None
            except:
                inbetriebnahme_parsed = None

            # Gespeicherte Anlage anlegen
            gespeicherte, created = GespeicherteAnlage.objects.get_or_create(
                liste=liste,
                anlagen_id=anlagen_id,
                defaults={
                    "anlagenname": anlagenname,
                    "energietraeger": energietraeger,
                    "leistung": leistung_parsed,
                    "bundesland": bundesland,
                    "ort": ort,
                    "plz": plz,
                    "status": status,
                    "technologie": technologie,
                    "betreiber": betreiber,
                    "inbetriebnahme": inbetriebnahme_parsed,
                    "notizen": notizen,
                },
            )

            if created:
                saved_count += 1
            else:
                already_exists_count += 1

        except Exception as e:
            # Bei Fehler mit der nächsten Anlage fortfahren
            continue

    # Erfolgsmeldung
    message = f"{saved_count} Anlagen erfolgreich gespeichert."
    if already_exists_count > 0:
        message += f" {already_exists_count} Anlagen waren bereits in der Liste."

    return JsonResponse(
        {"success": True, "message": message, "saved_count": saved_count, "already_exists_count": already_exists_count}
    )


def get_filter_params(request):
    """Extrahiert Filter-Parameter aus der Request"""
    return {
        "freitext": request.GET.get("freitext", ""),
        "energietraeger": request.GET.get("energietraeger", ""),
        "bundesland": request.GET.get("bundesland", ""),
        "leistung_min": request.GET.get("leistung_min", ""),
        "leistung_max": request.GET.get("leistung_max", ""),
        "status": request.GET.get("status", ""),
        "ort": request.GET.get("ort", ""),
        "plz": request.GET.get("plz", ""),
        "technologie": request.GET.get("technologie", ""),
        "art_solar": request.GET.get("art_solar", ""),
        "betreiber": request.GET.get("betreiber", ""),
        "datum_von": request.GET.get("datum_von", ""),
        "datum_bis": request.GET.get("datum_bis", ""),
        "radius_plz": request.GET.get("radius_plz", ""),
        "radius_km": request.GET.get("radius_km", ""),
    }


def get_empty_context():
    """Erstellt einen leeren Context für Fehlerfälle"""
    return {
        "energietraeger_list": [],
        "bundesland_list": [],
        "status_list": [],
        "technologie_list": [],
        "art_solar_list": [],
        "rows": [],
        "columns": [],
        "page_obj": None,
        "filter": {},
        "subscription": None,
        "can_export": False,
        "requests_remaining": 0,
        "max_filters": 3,
        "anlagen_listen": [],
        "can_save_lists": False,
        "map_data": "[]",
    }


def export_csv(request, **filter_params):
    """
    Exportiert die gefilterten Daten als CSV-Datei.
    Nur verfügbar für Premium-Tarif.
    """
    if not check_export_permission(request.user):
        return JsonResponse({"error": "Export nur im Premium-Tarif verfügbar"}, status=403)

    try:
        # SQL-Query mit den gleichen Filtern wie in data_view
        query = "SELECT * FROM test_Tabelle1 WHERE 1=1"
        params = []

        # Freitextsuche
        if filter_params["freitext"]:
            freitext = filter_params["freitext"]
            freitext_conditions = [
                "`Anzeige-Name der Einheit` LIKE ?",
                "`Energieträger` LIKE ?",
                "`Bundesland` LIKE ?",
                "`Ort` LIKE ?",
                "`Postleitzahl` LIKE ?",
                "`Name des Anlagenbetreibers (nur Org.)` LIKE ?",
                "`Technologie der Stromerzeugung` LIKE ?",
                "`Art der Solaranlage` LIKE ?",
                "`Betriebs-Status` LIKE ?",
            ]
            freitext_params = [f"%{freitext}%" for _ in freitext_conditions]
            query += " AND (" + " OR ".join(freitext_conditions) + ")"
            params.extend(freitext_params)

        if filter_params["energietraeger"]:
            query += " AND `Energieträger` = ?"
            params.append(filter_params["energietraeger"])
        if filter_params["bundesland"]:
            query += " AND `Bundesland` = ?"
            params.append(filter_params["bundesland"])
        if filter_params["leistung_min"]:
            query += " AND CAST(`Bruttoleistung der Einheit` AS REAL) >= ?"
            params.append(filter_params["leistung_min"])
        if filter_params["leistung_max"]:
            query += " AND CAST(`Bruttoleistung der Einheit` AS REAL) <= ?"
            params.append(filter_params["leistung_max"])
        if filter_params["status"]:
            query += " AND `Betriebs-Status` = ?"
            params.append(filter_params["status"])
        if filter_params["ort"]:
            query += " AND `Ort` LIKE ?"
            params.append(f"%{filter_params['ort']}%")
        if filter_params["plz"]:
            query += " AND `Postleitzahl` LIKE ?"
            params.append(f"%{filter_params['plz']}%")
        if filter_params["technologie"]:
            query += " AND `Technologie der Stromerzeugung` = ?"
            params.append(filter_params["technologie"])
        if filter_params["art_solar"]:
            query += " AND `Art der Solaranlage` = ?"
            params.append(filter_params["art_solar"])
        if filter_params["betreiber"]:
            query += " AND `Name des Anlagenbetreibers (nur Org.)` LIKE ?"
            params.append(f"%{filter_params['betreiber']}%")
        if filter_params["datum_von"]:
            query += " AND date(`Inbetriebnahmedatum der Einheit`) >= date(?)"
            params.append(filter_params["datum_von"])
        if filter_params["datum_bis"]:
            query += " AND date(`Inbetriebnahmedatum der Einheit`) <= date(?)"
            params.append(filter_params["datum_bis"])

        # Daten aus der Datenbank holen
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()
            columns = [desc[0] for desc in c.description]

            # Spaltennamen übersetzen
            columns = translate_column_names(columns)

        # Umkreissuche anwenden, falls angegeben
        if filter_params["radius_plz"] and filter_params["radius_km"]:
            target_coords = get_coordinates_for_plz(filter_params["radius_plz"])
            if target_coords:
                filtered_rows = []
                radius_km = float(filter_params["radius_km"])

                # Hole die ursprünglichen Spaltennamen für die Umkreissuche
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM test_Tabelle1 LIMIT 1")
                    original_columns = [desc[0] for desc in cursor.description]

                # Koordinaten-Spalten finden
                lat_index = None
                lon_index = None
                for i, col in enumerate(original_columns):
                    if "Koordinate: Breitengrad (WGS84)" in col:
                        lat_index = i
                    elif "Koordinate: Längengrad (WGS84)" in col:
                        lon_index = i

                for row in rows:
                    try:
                        if lat_index is not None and lon_index is not None:
                            lat_str = row[lat_index]
                            lon_str = row[lon_index]

                            if lat_str and lon_str and lat_str.strip() and lon_str.strip():
                                lat = float(lat_str)
                                lon = float(lon_str)

                                # Distanz berechnen
                                distance = haversine_distance(target_coords["lat"], target_coords["lon"], lat, lon)

                                # Nur Einträge im Radius hinzufügen
                                if distance <= radius_km:
                                    row_with_distance = list(row) + [f"{distance:.1f} km"]
                                    filtered_rows.append(row_with_distance)
                    except (ValueError, IndexError):
                        continue

                rows = filtered_rows
                columns = columns + ["Distanz"]

        # CSV-Datei erstellen
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="mastr_leads.csv"'

        # UTF-8 BOM für Excel-Kompatibilität
        response.write("\ufeff")

        writer = csv.writer(response, delimiter=";")

        # Header schreiben
        writer.writerow(columns)

        # Daten schreiben
        for row in rows:
            writer.writerow(row)

        # Export loggen
        log_request(request.user, "export_csv", filter_params)

        return response

    except Exception as e:
        log_request(request.user, "export_csv", filter_params, success=False, error_message=str(e))
        return HttpResponse(f"Export-Fehler: {str(e)}", status=500)


def home(request):
    """Optimierte Homepage für bessere Conversion"""
    if request.user.is_authenticated:
        return redirect("dashboard:data")
    
    # Hole Subscription-Pläne für die Anzeige
    from subscriptions.models import SubscriptionPlan
    plans = SubscriptionPlan.objects.all().order_by("price")
    
    context = {
        "plans": plans,
    }
    return render(request, "dashboard/landing.html", context)


@login_required
def charts_view(request):
    """Platzhalter für Charts-View"""
    return render(request, "dashboard/charts.html")


@login_required
def api_data(request):
    """Platzhalter für API-View"""
    return JsonResponse({"status": "success", "data": []})


@login_required
def api_chart_data(request):
    """Platzhalter für Chart-API-View"""
    return JsonResponse({"status": "success", "chart_data": {}})


@login_required
def export_data(request):
    """Export-View für Datenexport"""
    return export_csv(request, **get_filter_params(request))


def impressum_view(request):
    """Impressum-Seite"""
    return render(request, "dashboard/impressum.html")


def hilfe_view(request):
    """Hilfe-Seite mit Bedienungsanleitung und CSV-Import-Tipps"""
    return render(request, "dashboard/hilfe.html")


def track_event(request):
    """API-Endpunkt zum Tracken von Nutzerinteraktionen"""
    if request.method == "POST":
        try:
            event_type = request.POST.get("event_type")
            event_name = request.POST.get("event_name")
            page_url = request.POST.get("page_url", request.get_full_path())

            # Erstelle Analytics-Eintrag
            # analytics = UserAnalytics.objects.create(
            #     user=request.user if request.user.is_authenticated else None,
            #     session_id=request.session.session_key,
            #     event_type=event_type,
            #     event_name=event_name,
            #     page_url=page_url,
            #     user_agent=request.META.get('HTTP_USER_AGENT', ''),
            #     ip_address=request.META.get('REMOTE_ADDR', ''),
            #     additional_data=request.POST.dict()
            # )

            return JsonResponse({"status": "success", "id": "analytics_id_placeholder"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Nur POST-Requests erlaubt"}, status=405)


@login_required
def analytics_dashboard(request):
    """Analytics-Dashboard für Administratoren"""
    if not request.user.is_staff:
        messages.error(request, "Zugriff verweigert. Nur Administratoren können das Analytics-Dashboard einsehen.")
        return redirect("dashboard:data")

    # Zeitraum für die Analyse (letzte 30 Tage)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Hole Analytics-Daten
    # analytics_data = UserAnalytics.objects.filter(
    #     timestamp__range=(start_date, end_date)
    # )

    # Gruppiere nach Event-Typ
    # event_counts = {}
    # button_clicks = {}
    # page_views = {}
    # user_activity = {}

    # for entry in analytics_data:
    #     # Event-Typ-Zählung
    #     event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1
    #
    #     # Button-Klicks
    #     if entry.event_type == 'button_click':
    #         button_clicks[entry.event_name] = button_clicks.get(entry.event_name, 0) + 1
    #
    #     # Seitenaufrufe
    #     if entry.event_type == 'page_view':
    #         page_views[entry.page_url] = page_views.get(entry.page_url, 0) + 1
    #
    #     # Benutzeraktivität
    #     if entry.user:
    #         user_activity[entry.user.username] = user_activity.get(entry.user.username, 0) + 1

    # # Top 10 Button-Klicks
    # top_buttons = sorted(button_clicks.items(), key=lambda x: x[1], reverse=True)[:10]
    #
    # # Top 10 Seitenaufrufe
    # top_pages = sorted(page_views.items(), key=lambda x: x[1], reverse=True)[:10]
    #
    # # Top 10 aktive Benutzer
    # top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    #
    # # Tägliche Aktivität
    # daily_activity = {}
    # for entry in analytics_data:
    #     date = entry.timestamp.date()
    #     daily_activity[date] = daily_activity.get(date, 0) + 1
    #
    # daily_activity = dict(sorted(daily_activity.items()))

    context = {
        # 'total_events': analytics_data.count(),
        # 'event_counts': event_counts,
        # 'top_buttons': top_buttons,
        # 'top_pages': top_pages,
        # 'top_users': top_users,
        # 'daily_activity': daily_activity,
        # 'start_date': start_date,
        # 'end_date': end_date,
    }

    return render(request, "dashboard/analytics.html", context)


@login_required
def betreiber_view(request):
    """
    View für die Anlagenbetreiber-Ansicht - Alle Betreiber aus der externen MaStR-Datenbank
    
    Diese View zeigt alle Betreiber aus der MaStR-Datenbank an, mit Filter- und 
    Paginierungsfunktionen. Die Daten werden direkt aus der externen SQLite-Datenbank 
    gelesen, nicht aus dem Django ORM.
    
    Args:
        request: HTTP-Request-Objekt mit GET-Parametern für Filter
        
    Returns:
        Rendered Template mit Betreiber-Liste und Filter-Optionen
    """
    # Filter-Parameter aus URL holen
    name = request.GET.get("name", "")  # Name des Betreibers (Freitext-Suche)
    bundesland = request.GET.get("bundesland", "")  # Bundesland-Filter
    anzahl_min = request.GET.get("anzahl_min", "")  # Minimale Anzahl Anlagen
    anzahl_max = request.GET.get("anzahl_max", "")  # Maximale Anzahl Anlagen
    leistung_min = request.GET.get("leistung_min", "")  # Minimale Gesamtleistung
    leistung_max = request.GET.get("leistung_max", "")  # Maximale Gesamtleistung
    energietraeger = request.GET.get("energietraeger", "")  # Energieträger-Filter
    export = request.GET.get("export", "")  # Export-Flag (noch nicht implementiert)

    # Pfad zur externen MaStR-Datenbank
    data_db_path = os.path.join(settings.BASE_DIR, "data", "data.sqlite")
    
    # Debug: Prüfe ob Datei existiert
    print(f"[DEBUG] Datenbank-Pfad: {data_db_path}")
    print(f"[DEBUG] Datei existiert: {os.path.exists(data_db_path)}")
    
    # Direkte SQLite-Verbindung verwenden (nicht Django ORM)
    import sqlite3
    
    try:
        # Verbindung zur externen Datenbank herstellen
        with sqlite3.connect(data_db_path) as conn:
            # SQLite-Row-Factory für einfachere Datenverarbeitung
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Basis-SQL-Query für alle Betreiber aus der externen Datenbank
            # Gruppiert nach Betreibernummer und aggregiert Anlagen-Daten
            query = """
            SELECT 
                "MaStR-Nr. des Anlagenbetreibers" as betreibernummer,
                "Name des Anlagenbetreibers (nur Org.)" as name,
                COUNT("MaStR-Nr. der Einheit") as anzahl_anlagen,
                SUM(CAST("Bruttoleistung der Einheit" AS REAL)) as gesamtleistung,
                GROUP_CONCAT(DISTINCT "Bundesland") as bundeslaender,
                GROUP_CONCAT(DISTINCT "Ort") as orte,
                GROUP_CONCAT(DISTINCT "Energieträger") as energietraeger_liste
            FROM test_Tabelle1 
            WHERE "MaStR-Nr. des Anlagenbetreibers" IS NOT NULL 
            AND "MaStR-Nr. des Anlagenbetreibers" != ''
            """
            
            # Parameter und WHERE-Klauseln für dynamische Filter
            params = []
            where_clauses = []
            
            # Filter für Betreibername (LIKE-Suche)
            if name:
                where_clauses.append('"Name des Anlagenbetreibers (nur Org.)" LIKE ?')
                params.append(f"%{name}%")
            
            # Filter für Bundesland (exakte Übereinstimmung)
            if bundesland:
                where_clauses.append('"Bundesland" = ?')
                params.append(bundesland)
            
            # Filter für Energieträger (exakte Übereinstimmung)
            if energietraeger:
                where_clauses.append('"Energieträger" = ?')
                params.append(energietraeger)
            
            # WHERE-Klauseln zur Query hinzufügen
            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)
            
            # GROUP BY für Aggregation
            query += """
            GROUP BY "MaStR-Nr. des Anlagenbetreibers", "Name des Anlagenbetreibers (nur Org.)"
            """
            
            # HAVING-Klausel für aggregierte Filter (nach GROUP BY)
            having_clauses = []
            
            # Filter für minimale Anzahl Anlagen
            if anzahl_min:
                having_clauses.append("COUNT(\"MaStR-Nr. der Einheit\") >= ?")
                params.append(int(anzahl_min))
            
            # Filter für maximale Anzahl Anlagen
            if anzahl_max:
                having_clauses.append("COUNT(\"MaStR-Nr. der Einheit\") <= ?")
                params.append(int(anzahl_max))
            
            # Filter für minimale Gesamtleistung
            if leistung_min:
                having_clauses.append("SUM(CAST(\"Bruttoleistung der Einheit\" AS REAL)) >= ?")
                params.append(float(leistung_min))
            
            # Filter für maximale Gesamtleistung
            if leistung_max:
                having_clauses.append("SUM(CAST(\"Bruttoleistung der Einheit\" AS REAL)) <= ?")
                params.append(float(leistung_max))
            
            # HAVING-Klauseln zur Query hinzufügen
            if having_clauses:
                query += " HAVING " + " AND ".join(having_clauses)
            
            # Sortierung: Nach Anzahl Anlagen absteigend, dann nach Name
            query += " ORDER BY anzahl_anlagen DESC, name"
            
            # Debug: Zeige Query und Parameter
            print(f"[DEBUG] SQL-Query: {query}")
            print(f"[DEBUG] Query-Parameter: {params}")
            
            # Query ausführen und Ergebnisse verarbeiten
            cursor.execute(query, params)
            rows = cursor.fetchall()
            # SQLite-Rows zu Dictionaries konvertieren
            betreiber_liste = [dict(row) for row in rows]
            
            print(f"[DEBUG] Anzahl gefundener Betreiber: {len(betreiber_liste)}")

            # Bundesländer-Liste für Filter-Dropdown laden
            cursor.execute("SELECT DISTINCT \"Bundesland\" FROM test_Tabelle1 WHERE \"Bundesland\" IS NOT NULL ORDER BY \"Bundesland\"")
            bundesland_list = [row[0] for row in cursor.fetchall()]
            
            # Energieträger-Liste für Filter-Dropdown laden
            cursor.execute("SELECT DISTINCT \"Energieträger\" FROM test_Tabelle1 WHERE \"Energieträger\" IS NOT NULL ORDER BY \"Energieträger\"")
            energietraeger_list = [row[0] for row in cursor.fetchall()]
            
            print(f"[DEBUG] Anzahl Bundesländer: {len(bundesland_list)}")
            print(f"[DEBUG] Anzahl Energieträger: {len(energietraeger_list)}")
    
    except Exception as e:
        # Fehlerbehandlung: Logging und Fallback-Werte
        print(f"[ERROR] Fehler in betreiber_view: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: Leere Listen bei Fehlern
        betreiber_liste = []
        bundesland_list = []
        energietraeger_list = []
    
    # Paginierung: 50 Betreiber pro Seite
    paginator = Paginator(betreiber_liste, 50)
    page = request.GET.get("page")
    try:
        betreiber_paginiert = paginator.page(page)
    except PageNotAnInteger:
        # Bei ungültiger Seitenzahl: erste Seite
        betreiber_paginiert = paginator.page(1)
    except EmptyPage:
        # Bei zu hoher Seitenzahl: letzte Seite
        betreiber_paginiert = paginator.page(paginator.num_pages)

    # Context für Template vorbereiten
    context = {
        "betreiber_liste": betreiber_paginiert,  # Paginierte Betreiber-Liste
        "filter_values": request.GET,  # Aktuelle Filter-Werte für Template
        "bundesland_list": bundesland_list,  # Bundesländer für Dropdown
        "energietraeger_list": energietraeger_list,  # Energieträger für Dropdown
    }

    # Koordinaten für Karte vorbereiten (vereinfacht - Zentrum Deutschland)
    # TODO: Bessere Koordinaten-Logik implementieren (PLZ-basiert)
    anlagen_json = []
    for b in betreiber_paginiert:
        # Versuche PLZ aus den Orten zu extrahieren für bessere Koordinaten
        orte = b.get("orte", "").split(",") if b.get("orte") else []
        lat = 51.3  # Standard: Zentrum Deutschland
        lon = 10.1
        
        # JSON-Daten für Karten-Marker
        anlagen_json.append({
            "name": b.get("name", "Unbekannt"),
            "betreibernummer": b.get("betreibernummer", ""),
            "anzahl_anlagen": b.get("anzahl_anlagen", 0),
            "gesamtleistung": b.get("gesamtleistung", 0),
            "bundeslaender": b.get("bundeslaender", ""),
            "energietraeger": b.get("energietraeger_liste", ""),
            "lat": lat,
            "lon": lon,
        })

    # JSON-Daten für JavaScript-Karte
    context["anlagen_json"] = json.dumps(anlagen_json)
    
    # Template rendern
    return render(request, "dashboard/betreiber.html", context)


@login_required
def betreiber_detail_view(request, betreibernummer):
    """
    Detail-View für einen einzelnen Betreiber mit allen seinen Anlagen
    
    Zeigt detaillierte Informationen zu einem spezifischen Betreiber und
    alle seine Anlagen in einer Tabelle an.
    
    Args:
        request: HTTP-Request-Objekt
        betreibernummer: MaStR-Nummer des Betreibers
        
    Returns:
        Rendered Template mit Betreiber-Details und Anlagen-Liste
        
    Raises:
        Http404: Wenn Betreiber nicht gefunden wird
    """
    betreiber = None
    anlagen = []

    # Pfad zur externen MaStR-Datenbank
    data_db_path = os.path.join(settings.BASE_DIR, "data", "data.sqlite")
    
    # Direkte SQLite-Verbindung verwenden
    import sqlite3
    
    with sqlite3.connect(data_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Betreiber-Infos aus der externen Datenbank holen
        # Aggregiert Daten über alle Anlagen des Betreibers
        cursor.execute(
            """
            SELECT 
                "MaStR-Nr. des Anlagenbetreibers" as betreibernummer,
                "Name des Anlagenbetreibers (nur Org.)" as name,
                COUNT("MaStR-Nr. der Einheit") as anzahl_anlagen,
                SUM(CAST("Bruttoleistung der Einheit" AS REAL)) as gesamtleistung,
                GROUP_CONCAT(DISTINCT "Bundesland") as bundeslaender,
                GROUP_CONCAT(DISTINCT "Ort") as orte,
                GROUP_CONCAT(DISTINCT "Energieträger") as energietraeger_liste
            FROM test_Tabelle1 
            WHERE "MaStR-Nr. des Anlagenbetreibers" = ?
            GROUP BY "MaStR-Nr. des Anlagenbetreibers", "Name des Anlagenbetreibers (nur Org.)"
        """,
        [betreibernummer],
        )
        row = cursor.fetchone()
        betreiber = dict(row) if row else None

        if betreiber:
            # Anlagen des Betreibers holen (alle Einzelanlagen)
            cursor.execute(
                """
                SELECT 
                    "MaStR-Nr. der Einheit",
                    "Anzeige-Name der Einheit",
                    "Energieträger",
                    "Bruttoleistung der Einheit",
                    "Ort",
                    "Postleitzahl",
                    "Bundesland",
                    "Betriebs-Status",
                    "Inbetriebnahmedatum der Einheit",
                    "Technologie der Stromerzeugung",
                    "Art der Solaranlage"
                FROM test_Tabelle1
                WHERE "MaStR-Nr. des Anlagenbetreibers" = ?
                ORDER BY "Bruttoleistung der Einheit" DESC
            """,
            [betreibernummer],
            )
            rows = cursor.fetchall()
            anlagen = [dict(row) for row in rows]

    # 404-Fehler wenn Betreiber nicht gefunden
    if not betreiber:
        raise Http404("Betreiber nicht gefunden")

    # Context für Template
    context = {
        "betreiber": betreiber,  # Betreiber-Informationen
        "anlagen": anlagen,  # Liste aller Anlagen des Betreibers
    }
    
    return render(request, "dashboard/betreiber_detail.html", context)


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Holt eine Zeile aus dem Cursor"""
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))


@login_required
def anlage_bearbeiten(request, anlage_id):
    """View zum Bearbeiten einer gespeicherten Anlage"""
    anlage = get_object_or_404(GespeicherteAnlage, id=anlage_id, liste__user=request.user)

    if request.method == "POST":
        # Anlagen-Daten aktualisieren
        anlage.prioritaet = request.POST.get("prioritaet", "mittel")
        anlage.anlagenstatus = request.POST.get("anlagenstatus", "neu")
        anlage.benutzer_notizen = request.POST.get("benutzer_notizen", "")
        anlage.save()

        messages.success(request, "Anlage erfolgreich aktualisiert.")
        return redirect("dashboard:liste_detail", liste_id=anlage.liste.id)

    context = {
        "anlage": anlage,
        "prioritaet_choices": GespeicherteAnlage.PRIORITAET_CHOICES,
        "anlagenstatus_choices": GespeicherteAnlage.ANLAGENSTATUS_CHOICES,
    }
    return render(request, "dashboard/anlage_bearbeiten.html", context)


@login_required
def anlagen_verwaltung(request):
    """Übersicht aller Anlagen mit Filter- und Sortieroptionen"""
    # Filter-Parameter aus der URL
    prioritaet_filter = request.GET.get("prioritaet", "")
    status_filter = request.GET.get("status", "")
    liste_filter = request.GET.get("liste", "")
    sort_by = request.GET.get("sort", "-letzte_bearbeitung")

    # Basis-Query
    anlagen = GespeicherteAnlage.objects.filter(liste__user=request.user)

    # Filter anwenden
    if prioritaet_filter:
        anlagen = anlagen.filter(prioritaet=prioritaet_filter)
    if status_filter:
        anlagen = anlagen.filter(anlagenstatus=status_filter)
    if liste_filter:
        anlagen = anlagen.filter(liste_id=liste_filter)

    # Sortierung
    if sort_by not in [
        "anlagenname",
        "-anlagenname",
        "prioritaet",
        "-prioritaet",
        "anlagenstatus",
        "-anlagenstatus",
        "letzte_bearbeitung",
        "-letzte_bearbeitung",
    ]:
        sort_by = "-letzte_bearbeitung"

    anlagen = anlagen.order_by(sort_by)

    # Paginierung
    paginator = Paginator(anlagen, 20)
    page = request.GET.get("page")
    try:
        anlagen_page = paginator.page(page)
    except PageNotAnInteger:
        anlagen_page = paginator.page(1)
    except EmptyPage:
        anlagen_page = paginator.page(paginator.num_pages)

    # Listen für Filter-Dropdown
    listen = AnlagenListe.objects.filter(user=request.user).order_by("name")

    context = {
        "anlagen": anlagen_page,
        "listen": listen,
        "prioritaet_choices": GespeicherteAnlage.PRIORITAET_CHOICES,
        "anlagenstatus_choices": GespeicherteAnlage.ANLAGENSTATUS_CHOICES,
        "current_filters": {
            "prioritaet": prioritaet_filter,
            "status": status_filter,
            "liste": liste_filter,
            "sort": sort_by,
        },
        "stats": {
            "total": anlagen.count(),
            "neu": anlagen.filter(anlagenstatus="neu").count(),
            "kontaktiert": anlagen.filter(anlagenstatus="kontaktiert").count(),
            "in_bearbeitung": anlagen.filter(anlagenstatus="in_bearbeitung").count(),
            "abgeschlossen": anlagen.filter(anlagenstatus="abgeschlossen").count(),
        },
    }
    return render(request, "dashboard/anlagen_verwaltung.html", context)


@login_required
@require_POST
def anlage_status_update(request, anlage_id):
    """AJAX-View zum schnellen Aktualisieren des Anlagenstatus"""
    anlage = get_object_or_404(GespeicherteAnlage, id=anlage_id, liste__user=request.user)

    new_status = request.POST.get("status")
    if new_status in dict(GespeicherteAnlage.ANLAGENSTATUS_CHOICES):
        anlage.anlagenstatus = new_status
        anlage.save()
        return JsonResponse(
            {
                "success": True,
                "status": new_status,
                "status_display": anlage.get_anlagenstatus_display(),
                "status_color": anlage.get_status_color(),
            }
        )

    return JsonResponse({"success": False, "error": "Ungültiger Status"})


@login_required
@require_POST
def anlage_prioritaet_update(request, anlage_id):
    """AJAX-View zum schnellen Aktualisieren der Priorität"""
    anlage = get_object_or_404(GespeicherteAnlage, id=anlage_id, liste__user=request.user)

    new_prioritaet = request.POST.get("prioritaet")
    if new_prioritaet in dict(GespeicherteAnlage.PRIORITAET_CHOICES):
        anlage.prioritaet = new_prioritaet
        anlage.save()
        return JsonResponse(
            {
                "success": True,
                "prioritaet": new_prioritaet,
                "prioritaet_display": anlage.get_prioritaet_display(),
                "prioritaet_color": anlage.get_prioritaet_color(),
            }
        )

    return JsonResponse({"success": False, "error": "Ungültige Priorität"})


@login_required
@require_POST
def anlage_notiz_update(request, anlage_id):
    """AJAX-View zum Aktualisieren der Benutzer-Notizen"""
    anlage = get_object_or_404(GespeicherteAnlage, id=anlage_id, liste__user=request.user)

    notiz = request.POST.get("notiz", "")
    anlage.benutzer_notizen = notiz
    anlage.save()

    return JsonResponse({"success": True, "notiz": notiz})


@login_required
def anlagen_export(request):
    """Export aller Anlagen mit benutzerdefinierten Eigenschaften"""
    if not check_export_permission(request.user):
        messages.error(request, "CSV-Export ist nur im Premium-Tarif verfügbar.")
        return redirect("dashboard:anlagen_verwaltung")

    # Filter-Parameter
    prioritaet_filter = request.GET.get("prioritaet", "")
    status_filter = request.GET.get("status", "")
    liste_filter = request.GET.get("liste", "")

    anlagen = GespeicherteAnlage.objects.filter(liste__user=request.user)

    if prioritaet_filter:
        anlagen = anlagen.filter(prioritaet=prioritaet_filter)
    if status_filter:
        anlagen = anlagen.filter(anlagenstatus=status_filter)
    if liste_filter:
        anlagen = anlagen.filter(liste_id=liste_filter)

    # CSV-Response erstellen
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="anlagen_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )

    # BOM für korrekte UTF-8-Darstellung in Excel
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")

    # Header
    writer.writerow(
        [
            "Anlagen-ID",
            "Anlagenname",
            "Energieträger",
            "Leistung (kW)",
            "Bundesland",
            "Ort",
            "PLZ",
            "Betriebs-Status",
            "Technologie",
            "Betreiber",
            "Inbetriebnahme",
            "Liste",
            "Priorität",
            "Anlagenstatus",
            "Benutzer-Notizen",
            "Hinzugefügt am",
            "Letzte Bearbeitung",
        ]
    )

    # Daten
    for anlage in anlagen:
        writer.writerow(
            [
                anlage.anlagen_id,
                anlage.anlagenname,
                anlage.energietraeger,
                anlage.leistung or "",
                anlage.bundesland,
                anlage.ort,
                anlage.plz,
                anlage.status,
                anlage.technologie,
                anlage.betreiber,
                anlage.inbetriebnahme.strftime("%d.%m.%Y") if anlage.inbetriebnahme else "",
                anlage.liste.name,
                anlage.get_prioritaet_display(),
                anlage.get_anlagenstatus_display(),
                anlage.benutzer_notizen,
                anlage.hinzugefuegt_am.strftime("%d.%m.%Y %H:%M"),
                anlage.letzte_bearbeitung.strftime("%d.%m.%Y %H:%M"),
            ]
        )

    return response


def translate_column_names(columns):
    """Übersetzt Datenbank-Spaltennamen in benutzerfreundliche Namen"""
    column_translations = {
        "MaStR-Nr. der Einheit": "MaStR-Nr.",
        "Anzeige-Name der Einheit": "Anlagenname",
        "Betriebs-Status": "Status",
        "Energieträger": "Energieträger",
        "Bruttoleistung der Einheit": "Leistung (kW)",
        "Nettonennleistung der Einheit": "Nettoleistung (kW)",
        "Inbetriebnahmedatum der Einheit": "Inbetriebnahme",
        "Registrierungsdatum der Einheit": "Registrierung",
        "Bundesland": "Bundesland",
        "Postleitzahl": "PLZ",
        "Ort": "Ort",
        "Straße": "Straße",
        "Hausnummer": "Hausnummer",
        "Gemarkung": "Gemarkung",
        "Flurstück": "Flurstück",
        "Gemeindeschlüssel": "Gemeindeschlüssel",
        "Gemeinde": "Gemeinde",
        "Landkreis": "Landkreis",
        "Koordinate: Breitengrad (WGS84)": "Breitengrad",
        "Koordinate: Längengrad (WGS84)": "Längengrad",
        "Technologie der Stromerzeugung": "Technologie",
        "Art der Solaranlage": "Solarart",
        "Anzahl der Solar-Module": "Anzahl Module",
        "Hauptausrichtung der Solar-Module": "Ausrichtung",
        "Art der Bodenfläche (der PV-Anlage)": "Bodenfläche",
        "Name des Windparks": "Windpark",
        "Wind an Land oder auf See": "Windstandort",
        "Nabenhöhe der Windenergieanlage": "Nabenhöhe",
        "Rotordurchmesser der Windenergieanlage": "Rotordurchmesser",
        "Hersteller der Windenergieanlage": "Hersteller",
        "Typenbezeichnung": "Typ",
        "Hauptbrennstoff der Einheit": "Brennstoff",
        "MaStR-Nr. der Speichereinheit": "Speicher-MaStR-Nr.",
        "Speichertechnologie": "Speichertechnologie",
        "Nutzbare Speicherkapazität in kWh": "Speicherkapazität",
        "Letzte Aktualisierung": "Aktualisierung",
        "Datum der endgültigen Stilllegung": "Stilllegung",
        "Datum der geplanten Inbetriebnahme": "Geplante Inbetriebnahme",
        "Name des Anlagenbetreibers (nur Org.)": "Betreiber",
        "MaStR-Nr. des Anlagenbetreibers": "Betreiber-MaStR-Nr.",
        "Volleinspeisung oder Teileinspeisung": "Einspeisung",
        "MaStR-Nr. der Genehmigung": "Genehmigung-MaStR-Nr.",
        "Name des Anschluss-Netzbetreibers": "Netzbetreiber",
        "MaStR-Nr. des Anschluss-Netzbetreibers": "Netzbetreiber-MaStR-Nr.",
        "Netzbetreiberprüfung": "Netzbetreiberprüfung",
        "Spannungsebene": "Spannungsebene",
        "MaStR-Nr. der Lokation": "Lokation-MaStR-Nr.",
        "MaStR-Nr. der EEG-Anlage": "EEG-MaStR-Nr.",
        "EEG-Anlagenschlüssel": "EEG-Schlüssel",
        "Inbetriebnahmedatum der EEG-Anlage": "EEG-Inbetriebnahme",
        "Installierte Leistung der EEG-Anlage": "EEG-Leistung",
        "Zuschlagnummer (EEG/KWK-Ausschreibung)": "Zuschlagnummer",
        "MaStR-Nr. der KWK-Anlage": "KWK-MaStR-Nr.",
        "Inbetriebnahmedatum der KWK-Anlage": "KWK-Inbetriebnahme",
        "Elektrische KWK-Leistung": "KWK-Leistung",
        "Thermische Nutzleistung in kW": "Thermische Leistung",
        "Distanz": "Distanz",
    }

    translated_columns = []
    for column in columns:
        translated_columns.append(column_translations.get(column, column))

    return translated_columns


# API ViewSets
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import GespeicherteAnlageSerializer, AnlagenListeSerializer, UserSerializer


class GespeicherteAnlageViewSet(viewsets.ModelViewSet):
    """API ViewSet für gespeicherte Anlagen"""
    queryset = GespeicherteAnlage.objects.all()
    serializer_class = GespeicherteAnlageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtert Anlagen nach dem aktuellen Benutzer"""
        return self.queryset.filter(liste__user=self.request.user)


class AnlagenListeViewSet(viewsets.ModelViewSet):
    """API ViewSet für Anlagenlisten"""
    queryset = AnlagenListe.objects.all()
    serializer_class = AnlagenListeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtert Listen nach dem aktuellen Benutzer"""
        return self.queryset.filter(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet für Benutzer (nur Lesen)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Zeigt nur den aktuellen Benutzer"""
        return User.objects.filter(id=self.request.user.id)



