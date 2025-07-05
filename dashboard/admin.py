from django.contrib import admin
from .models import AnlagenListe, GespeicherteAnlage

@admin.register(AnlagenListe)
class AnlagenListeAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'erstellt_am', 'aktualisiert_am', 'anzahl_anlagen']
    list_filter = ['erstellt_am', 'aktualisiert_am']
    search_fields = ['name', 'user__username']

    def anzahl_anlagen(self, obj):
        return obj.anlagen.count()
    anzahl_anlagen.short_description = 'Anzahl Anlagen'

@admin.register(GespeicherteAnlage)
class GespeicherteAnlageAdmin(admin.ModelAdmin):
    list_display = ['anlagenname', 'anlagen_id', 'liste', 'energietraeger', 'leistung', 'ort', 'hinzugefuegt_am']
    list_filter = ['energietraeger', 'bundesland', 'hinzugefuegt_am']
    search_fields = ['anlagenname', 'anlagen_id', 'liste__name']
    date_hierarchy = 'hinzugefuegt_am'

