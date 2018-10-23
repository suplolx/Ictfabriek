from django.db import models

from django.db import models
from django.urls import reverse

import datetime
from django.contrib.auth.models import User
from django.utils import timezone


class Klant(models.Model):
    class Meta:
        verbose_name_plural = "Klanten"

    klant_voornaam = models.CharField(max_length=50)
    klant_achternaam = models.CharField(max_length=50)
    klant_telefoonnummer = models.CharField(max_length=40)
    klant_straatnaam = models.CharField(max_length=100, blank=True, null=True)
    klant_huisnummer = models.IntegerField(blank=True, null=True)
    klant_postcode = models.CharField(max_length=7, blank=True, null=True)
    klant_woonplaats = models.CharField(max_length=70, blank=True, null=True)
    klant_emailadres = models.CharField(max_length=150, blank=True, null=True)
    klant_datum_aangepast = models.DateTimeField('Datum aangepast', null=True)
    klant_aangepast_door = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)

    def get_apparaten(self):
        return self.apparaat_set.all()

    def heeft_apparaten(self):
        return len(self.apparaat_set.all()) > 0

    def get_tickets(self):
        return self.ticket_set.all()

    def heeft_tickets(self):
        return len(self.ticket_set.all()) > 0
    
    def get_aantal_tickets(self):
        return len(self.ticket_set.all())

    def get_absolute_url(self):
        return reverse('tickets:nieuw_apparaat', kwargs={'pk': self.pk})

    def __str__(self):
        return "{} {}".format(self.klant_voornaam, self.klant_achternaam)


class Apparaat(models.Model):
    class Meta:
        verbose_name_plural = "Apparaten"

    apparaat_merk = models.CharField(max_length=50)
    apparaat_type = models.CharField(max_length=100, blank=True, null=True)
    apparaat_serienummer = models.CharField(max_length=75, blank=True, null=True)
    apparaat_staat = models.CharField(max_length=250)
    apparaat_accessoires = models.CharField(max_length=250, blank=True, null=True)
    apparaat_klant = models.ForeignKey(Klant, on_delete=models.CASCADE, blank=True, null=True)

    def heeft_meer_tickets(self):
        return len(self.ticket_set.all()) > 1

    def get_tickets(self):
        return self.ticket_set.all()

    def heeft_accessoires(self):
        return self.apparaat_accessoires is not None

    def get_absolute_url(self):
        return reverse('tickets:klant_detail', kwargs={'pk': self.apparaat_klant.id})

    def __str__(self):
        return "{} {}".format(self.apparaat_merk, self.apparaat_type)


class Ticket(models.Model):
    PRIORITEIT_KEUZES = (
        ('laag', 'Laag'),
        ('normaal', 'Normaal'),
        ('hoog', 'Hoog')
    )
    STATUS_KEUZES = (
        ('In behandeling', 'In behandeling'),
        ('Afgesloten', 'Afgesloten'),
        ('Wachten op onderdelen', 'Wachten op onderdelen'),
        ('Wachten op reactie klant', 'Wachten op reactie klant'),
    )

    ticket_prioriteit = models.CharField(
        max_length=50,
        choices=PRIORITEIT_KEUZES,
        default='Normaal',
    )
    ticket_status = models.CharField(
        max_length=50,
        choices=STATUS_KEUZES,
        default="In behandeling",
    )
    ticket_onderwerp = models.CharField(max_length=100)
    ticket_body = models.CharField(max_length=1000)
    ticket_datum_aangemaakt = models.DateTimeField('datum aangemaakt')
    ticket_datum_aangepast = models.DateTimeField('datum aangepast', null=True)
    ticket_datum_verwijderd = models.DateTimeField('datum verwijderd', null=True)
    ticket_auteur = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    ticket_auteur_bewerkt = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='+')
    ticket_klant = models.ForeignKey(Klant, on_delete=models.CASCADE, blank=True, null=True)
    ticket_apparaat = models.ForeignKey(Apparaat, on_delete=models.SET_NULL, blank=True, null=True)

    def heeft_facturen(self):
        return len(self.factuur_set.all()) > 0

    def get_facturen(self):
        return self.factuur_set.all()

    def is_in_behandeling(self):
        return self.ticket_status == "In behandeling"

    def recent_aangemaakt(self):
        return self.ticket_datum_aangemaakt >= timezone.now() - datetime.timedelta(days=1)

    def recent_aangepast(self):
        return self.ticket_datum_aangepast >= timezone.now() - datetime.timedelta(days=1)

    def get_absolute_url(self):
        return reverse('tickets:detail', kwargs={'pk': self.pk})

    def get_apparaten(self):
        return self.ticket_apparaat.ticket_set.all()

    def __str__(self):
        return "Ticket nummer: {} '{}'".format(self.id, self.ticket_onderwerp)


class Opmerking(models.Model):
    class Meta:
        verbose_name_plural = "Opmerkingen"

    opmerking_type = models.CharField(max_length=25, default="informatie")
    opmerking_body = models.CharField(max_length=500, default="Geen")
    opmerking_datum_aangemaakt = models.DateTimeField('datum aangemaakt')
    opmerking_auteur = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    opmerking_ontvanger = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='+')
    opmerking_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def heeft_antwoorden(self):
        return len(self.antwoord_set.all()) > 0

    def get_antwoorden(self):
        return self.antwoord_set.all()

    def __str__(self):
        return self.opmerking_body + " - " + self.opmerking_type


class Antwoord(models.Model):
    class Meta:
        verbose_name_plural = "Antwoorden"

    antwoord_body = models.CharField(max_length=500, default="Geen")
    antwoord_datum_aangemaakt = models.DateTimeField('datum aangemaakt')
    antwoord_auteur = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    antwoord_opmerking = models.ForeignKey(Opmerking, on_delete=models.CASCADE)

    def __str__(self):
        return self.antwoord_body


class Notificatie(models.Model):
    notificatie_body = models.CharField(max_length=250)
    notificatie_van = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    notificatie_naar = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='+')
    notificatie_datum_aangemaakt = models.DateTimeField('datum aangemaakt')
    notificatie_gezien = models.BooleanField(default=False)
    notificatie_opmerking = models.ForeignKey(Opmerking, on_delete=models.CASCADE, blank=True, null=True)
    notificatie_antwoord = models.ForeignKey(Antwoord, on_delete=models.CASCADE, null=True, blank=True)

    def heeft_gezien(self):
        return self.notificatie_gezien

    def __str__(self):
        return self.notificatie_body


class Artikel(models.Model):
    class Meta:
        verbose_name_plural = "Artikelen"

    artikel_naam = models.CharField(max_length=70)
    artikel_prijs = models.DecimalField(max_digits=50, decimal_places=2)
    artikel_omschrijving = models.CharField(max_length=250)

    def __str__(self):
        return self.artikel_naam


class Factuur(models.Model):
    class Meta:
        verbose_name_plural = "Facturen"

    factuur_ticket = models.ForeignKey(Ticket, models.SET_NULL, blank=True, null=True)
    factuur_klant = models.ForeignKey(Klant, on_delete=models.CASCADE)
    factuur_artikelen = models.ManyToManyField(Artikel)
    factuur_aangemaakt_door = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    factuur_datum_aangemaakt = models.DateTimeField('datum_aangemaakt')
    factuur_werkzaamheden = models.CharField(max_length=10000, blank=True, default="Geen klacht geconstateerd")
    factuur_pdf_file = models.FileField(upload_to='facturen/', blank=True, null=True)

    def get_artikelen(self):
        return self.factuur_artikelen.all()

    def get_extra_artikelen(self):
        return self.nieuwartikel_set.all()

    def get_totaal(self):
        artikel_prijzen = [artikel.artikel_prijs for artikel in self.get_artikelen()]
        extra_artikel_prijzen = [artikel.nieuw_artikel_prijs for artikel in self.get_extra_artikelen()]
        return sum(artikel_prijzen) + sum(extra_artikel_prijzen)

    def __str__(self):
        return "Factuur nummer " + str(self.id)


class NieuwArtikel(models.Model):
    class Meta:
        verbose_name_plural = "Nieuwe artikelen"

    nieuw_artikel_naam = models.CharField(max_length=100)
    nieuw_artikel_prijs = models.DecimalField(max_digits=10, decimal_places=2)
    nieuw_artikel_omschrijving = models.CharField(max_length=200, blank=True, null=True)
    nieuw_artikel_toegev_door = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    nieuw_artikel_datum_toegev = models.DateTimeField('datum aangemaakt')
    nieuw_artikel_factuur = models.ForeignKey(Factuur, on_delete=models.CASCADE)

    def __str__(self):
        return self.nieuw_artikel_naam
