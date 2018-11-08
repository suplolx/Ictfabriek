from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField, ModelSerializer

from django.contrib.auth.models import User
from tickets.models import (
    Klant, Apparaat, Ticket, Opmerking
)

from django.utils.timezone import now


class KlantSerializer(HyperlinkedModelSerializer):
    
    klant_aangepast_door = SerializerMethodField()
    
    class Meta:
        model = Klant
        fields = (
            'url',
            'id', 
            'klant_voornaam',
            'klant_achternaam',
            'klant_telefoonnummer',
            'klant_straatnaam',
            'klant_huisnummer',
            'klant_postcode',
            'klant_woonplaats',
            'klant_emailadres',
            'klant_datum_aangepast',
            'klant_aangepast_door',
            )

    def get_klant_aangepast_door(self, obj):
        if obj.klant_aangepast_door:
            return str(obj.klant_aangepast_door.username)


class ApparaatSerializer(HyperlinkedModelSerializer):
    
    klant_naam = SerializerMethodField()
    
    class Meta:
        model = Apparaat
        fields = (
            'url',
            'id',
            'apparaat_merk',
            'apparaat_type',
            'apparaat_serienummer',
            'apparaat_staat',
            'apparaat_accessoires',
            'apparaat_klant',
            'klant_naam'
        )
    
    def get_klant_naam(self, obj):
        if obj.apparaat_klant:
            return str(obj.apparaat_klant.klant_voornaam) + " " + str(obj.apparaat_klant.klant_achternaam)


class TicketSerializer(HyperlinkedModelSerializer):
    
    auteur_naam = SerializerMethodField()
    auteur_naam_bewerkt = SerializerMethodField()
    klant_naam = SerializerMethodField()
    dagen = SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            'url',
            'id',
            'ticket_onderwerp',
            'ticket_body',
            'ticket_datum_aangemaakt',
            'ticket_datum_aangepast',
            'ticket_datum_verwijderd',
            'auteur_naam',
            'auteur_naam_bewerkt',
            'ticket_klant',
            'ticket_apparaat',
            'klant_naam',
            'dagen',
        )

    def get_auteur_naam(self, obj):
        if obj.ticket_auteur:
            return str(obj.ticket_auteur.username)

    def get_auteur_naam_bewerkt(self, obj):
        if obj.ticket_auteur_bewerkt:
            return str(obj.ticket_auteur_bewerkt.username)

    def get_klant_naam(self, obj):
        if obj.ticket_klant:
            return str(obj.ticket_klant.klant_voornaam) + " " + str(obj.ticket_klant.klant_achternaam)

    def get_dagen(self, obj):
        if obj.ticket_datum_aangemaakt:
            return (now() - obj.ticket_datum_aangemaakt).days


class UserSerializer(ModelSerializer):
    
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'first_name',
            'last_name', 
            'password',
        )
        extra_kwargs = {"password": {
            
                "write_only": True,    
            }
        }

    def create(self, validated_data):
        username = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        password = validated_data['password']
        user_obj = User(username=username, first_name=first_name, last_name=last_name)
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class OpmerkingSerializer(HyperlinkedModelSerializer):
    
    auteur_naam = SerializerMethodField()
    
    class Meta:
        model = Opmerking
        fields = (
            'url',
            'id',
            'opmerking_type',
            'opmerking_body',
            'opmerking_datum_aangemaakt',
            'opmerking_auteur',
            'opmerking_ticket',
            'auteur_naam',
        )

    def get_auteur_naam(self, obj):
        if obj.opmerking_auteur:
            return str(obj.opmerking_auteur.username)
