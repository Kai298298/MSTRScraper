"""
Serializers für die Dashboard API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AnlagenListe, GespeicherteAnlage


class UserSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class AnlagenListeSerializer(serializers.ModelSerializer):
    """Serializer für Anlagenlisten"""
    user = UserSerializer(read_only=True)
    anlagen_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnlagenListe
        fields = ['id', 'name', 'beschreibung', 'user', 'erstellt_am', 'anlagen_count']
        read_only_fields = ['id', 'user', 'erstellt_am']
    
    def get_anlagen_count(self, obj):
        """Gibt die Anzahl der Anlagen in der Liste zurück"""
        return obj.gespeicherteanlage_set.count()


class GespeicherteAnlageSerializer(serializers.ModelSerializer):
    """Serializer für gespeicherte Anlagen"""
    liste = AnlagenListeSerializer(read_only=True)
    prioritaet_display = serializers.CharField(source='get_prioritaet_display', read_only=True)
    anlagenstatus_display = serializers.CharField(source='get_anlagenstatus_display', read_only=True)
    
    class Meta:
        model = GespeicherteAnlage
        fields = [
            'id', 'anlagen_id', 'anlagenname', 'energietraeger', 'leistung',
            'bundesland', 'ort', 'plz', 'status', 'technologie', 'betreiber',
            'inbetriebnahme', 'notizen', 'prioritaet', 'prioritaet_display',
            'anlagenstatus', 'anlagenstatus_display', 'benutzer_notizen',
            'liste', 'hinzugefuegt_am', 'letzte_bearbeitung'
        ]
        read_only_fields = ['id', 'hinzugefuegt_am', 'letzte_bearbeitung'] 