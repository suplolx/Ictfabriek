from django.contrib import admin

from .models import Ticket, Klant, Apparaat, Artikel, Factuur, Opmerking, Antwoord

admin.site.register(Ticket)
admin.site.register(Klant)
admin.site.register(Apparaat)
admin.site.register(Artikel)
admin.site.register(Factuur)
admin.site.register(Opmerking)
admin.site.register(Antwoord)
