from django.contrib.auth.models import User
from django.db import models


class PlantType(models.Model):
    """Typ der Anlage, z.B. Solar, Wind, etc."""

    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, default="fa-solar-panel")

    class Meta:
        verbose_name = "Anlagentyp"
        verbose_name_plural = "Anlagentypen"

    def __str__(self):
        return self.name


class Lead(models.Model):
    """
    Repräsentiert einen Lead aus dem Marktstammdatenregister.
    Enthält Informationen über den Betreiber und die Anlage.
    """

    company_name = models.CharField(max_length=255, verbose_name="Firmenname")
    street = models.CharField(max_length=255, verbose_name="Straße")
    zip_code = models.CharField(max_length=10, verbose_name="PLZ")
    city = models.CharField(max_length=100, verbose_name="Stadt")
    state = models.CharField(max_length=100, verbose_name="Bundesland")

    plant_type = models.ForeignKey(PlantType, on_delete=models.SET_NULL, null=True, related_name="leads")
    power_kw = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Leistung (kW)")
    commissioning_date = models.DateField(verbose_name="Inbetriebnahmedatum")

    contact_person = models.CharField(max_length=255, blank=True, verbose_name="Ansprechpartner")
    email = models.EmailField(blank=True, verbose_name="E-Mail")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ["-commissioning_date"]

    def __str__(self):
        return f"{self.company_name} - {self.plant_type}"


class SavedFilter(models.Model):
    """Gespeicherte Filter für Benutzer"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_filters")
    name = models.CharField(max_length=100)
    filters = models.JSONField()  # Speichert die Filter-Konfiguration
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gespeicherter Filter"
        verbose_name_plural = "Gespeicherte Filter"
        unique_together = ["user", "name"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class DashboardWidget(models.Model):
    """Widget-Konfigurationen für das Dashboard"""

    WIDGET_TYPES = [
        ("chart", "Chart"),
        ("table", "Tabelle"),
        ("metric", "Metrik"),
        ("map", "Karte"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dashboard_widgets")
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    configuration = models.JSONField()  # Widget-spezifische Konfiguration
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=6)  # Bootstrap grid columns
    height = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ["position_y", "position_x"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class AnlagenListe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="anlagen_listen")
    name = models.CharField(max_length=200, verbose_name="Listenname")
    beschreibung = models.TextField(blank=True, verbose_name="Beschreibung")
    erstellt_am = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    aktualisiert_am = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")

    class Meta:
        verbose_name = "Anlagen-Liste"
        verbose_name_plural = "Anlagen-Listen"
        ordering = ["-aktualisiert_am"]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class GespeicherteAnlage(models.Model):
    PRIORITAET_CHOICES = [
        ("niedrig", "Niedrig"),
        ("mittel", "Mittel"),
        ("hoch", "Hoch"),
        ("kritisch", "Kritisch"),
    ]

    ANLAGENSTATUS_CHOICES = [
        ("neu", "Neu"),
        ("kontaktiert", "Kontaktiert"),
        ("in_bearbeitung", "In Bearbeitung"),
        ("angebot_versendet", "Angebot versendet"),
        ("verhandlungen", "In Verhandlungen"),
        ("abgeschlossen", "Abgeschlossen"),
        ("abgelehnt", "Abgelehnt"),
        ("archiviert", "Archiviert"),
    ]

    liste = models.ForeignKey(AnlagenListe, on_delete=models.CASCADE, related_name="anlagen")
    anlagen_id = models.CharField(max_length=100, verbose_name="MaStR Anlagen-ID")
    anlagenname = models.CharField(max_length=500, verbose_name="Anlagenname")
    energietraeger = models.CharField(max_length=100, verbose_name="Energieträger")
    leistung = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Leistung (kW)")
    bundesland = models.CharField(max_length=100, verbose_name="Bundesland")
    ort = models.CharField(max_length=200, verbose_name="Ort")
    plz = models.CharField(max_length=10, verbose_name="PLZ")
    status = models.CharField(max_length=100, verbose_name="Betriebs-Status")
    technologie = models.CharField(max_length=200, blank=True, verbose_name="Technologie")
    betreiber = models.CharField(max_length=500, blank=True, verbose_name="Betreiber")
    inbetriebnahme = models.DateField(null=True, blank=True, verbose_name="Inbetriebnahme")
    hinzugefuegt_am = models.DateTimeField(auto_now_add=True, verbose_name="Hinzugefügt am")
    notizen = models.TextField(blank=True, verbose_name="Notizen")

    # Neue Felder für benutzerdefinierte Eigenschaften
    prioritaet = models.CharField(max_length=20, choices=PRIORITAET_CHOICES, default="mittel", verbose_name="Priorität")
    anlagenstatus = models.CharField(
        max_length=20, choices=ANLAGENSTATUS_CHOICES, default="neu", verbose_name="Anlagenstatus"
    )
    benutzer_notizen = models.TextField(blank=True, verbose_name="Benutzer-Notizen")
    letzte_bearbeitung = models.DateTimeField(auto_now=True, verbose_name="Letzte Bearbeitung")

    class Meta:
        verbose_name = "Gespeicherte Anlage"
        verbose_name_plural = "Gespeicherte Anlagen"
        ordering = ["-hinzugefuegt_am"]
        unique_together = ("liste", "anlagen_id")

    def __str__(self):
        return f"{self.anlagenname} ({self.anlagen_id}) in {self.liste.name}"

    def get_prioritaet_color(self):
        """Gibt die CSS-Klasse für die Prioritätsfarbe zurück"""
        colors = {
            "niedrig": "text-success",
            "mittel": "text-warning",
            "hoch": "text-danger",
            "kritisch": "text-danger fw-bold",
        }
        return colors.get(self.prioritaet, "text-secondary")

    def get_status_color(self):
        """Gibt die CSS-Klasse für die Statusfarbe zurück"""
        colors = {
            "neu": "badge bg-primary",
            "kontaktiert": "badge bg-info",
            "in_bearbeitung": "badge bg-warning",
            "angebot_versendet": "badge bg-secondary",
            "verhandlungen": "badge bg-warning text-dark",
            "abgeschlossen": "badge bg-success",
            "abgelehnt": "badge bg-danger",
            "archiviert": "badge bg-dark",
        }
        return colors.get(self.anlagenstatus, "badge bg-secondary")


class AnlagenFeedback(models.Model):
    """Feedback von Benutzern zu Anlagen-Daten"""

    FEEDBACK_TYP_CHOICES = [
        ("daten_fehler", "Datenfehler"),
        ("veraltete_daten", "Veraltete Daten"),
        ("fehlende_daten", "Fehlende Daten"),
        ("falsche_zuordnung", "Falsche Zuordnung"),
        ("sonstiges", "Sonstiges"),
    ]

    STATUS_CHOICES = [
        ("neu", "Neu"),
        ("in_bearbeitung", "In Bearbeitung"),
        ("geloest", "Gelöst"),
        ("abgelehnt", "Abgelehnt"),
    ]

    # Anlagen-Referenz (kann sowohl gespeicherte als auch MaStR-Anlagen betreffen)
    gespeicherte_anlage = models.ForeignKey(
        GespeicherteAnlage, on_delete=models.CASCADE, null=True, blank=True, related_name="feedback"
    )
    mastr_anlagen_id = models.CharField(max_length=100, blank=True, verbose_name="MaStR Anlagen-ID")

    # Feedback-Details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="anlagen_feedback")
    feedback_typ = models.CharField(max_length=20, choices=FEEDBACK_TYP_CHOICES, verbose_name="Feedback-Typ")
    titel = models.CharField(max_length=200, verbose_name="Titel")
    beschreibung = models.TextField(verbose_name="Beschreibung des Problems")
    vorgeschlagene_korrektur = models.TextField(blank=True, verbose_name="Vorgeschlagene Korrektur")

    # Status und Verwaltung
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="neu", verbose_name="Status")
    admin_antwort = models.TextField(blank=True, verbose_name="Admin-Antwort")
    admin_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_feedback"
    )

    # Zeitstempel
    erstellt_am = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    aktualisiert_am = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    geloest_am = models.DateTimeField(null=True, blank=True, verbose_name="Gelöst am")

    class Meta:
        verbose_name = "Anlagen-Feedback"
        verbose_name_plural = "Anlagen-Feedback"
        ordering = ["-erstellt_am"]

    def __str__(self):
        anlage_name = self.gespeicherte_anlage.anlagenname if self.gespeicherte_anlage else self.mastr_anlagen_id
        return f"Feedback zu {anlage_name} - {self.get_feedback_typ_display()}"

    def get_anlagen_id(self):
        """Gibt die Anlagen-ID zurück (entweder von gespeicherter Anlage oder MaStR)"""
        if self.gespeicherte_anlage:
            return self.gespeicherte_anlage.anlagen_id
        return self.mastr_anlagen_id

    def get_anlagen_name(self):
        """Gibt den Anlagennamen zurück"""
        if self.gespeicherte_anlage:
            return self.gespeicherte_anlage.anlagenname
        return f"MaStR Anlage {self.mastr_anlagen_id}"

    def get_status_color(self):
        """Gibt die CSS-Klasse für die Statusfarbe zurück"""
        colors = {
            "neu": "badge bg-primary",
            "in_bearbeitung": "badge bg-warning",
            "geloest": "badge bg-success",
            "abgelehnt": "badge bg-danger",
        }
        return colors.get(self.status, "badge bg-secondary")
