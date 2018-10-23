from django import forms
from django.contrib.auth.models import User
from .models import Ticket, Klant, Apparaat, Factuur, NieuwArtikel

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('ticket_onderwerp', 'ticket_body', 'ticket_prioriteit')
        widgets = {
            'ticket_body': forms.Textarea
        }


class KlantForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    klant_emailadres = forms.CharField(widget=forms.EmailField, required=False)
    class Meta:
        model = Klant
        fields = ('id', 'klant_voornaam', 'klant_achternaam', 'klant_telefoonnummer', 'klant_emailadres')


class ApparaatForm(forms.ModelForm):
    class Meta:
        model = Apparaat
        fields = (
            'apparaat_merk', 'apparaat_type',
            'apparaat_accessoires', 'apparaat_staat',
        )


class FactuurForm(forms.ModelForm):
    factuur_werkzaamheden = forms.CharField(widget=forms.Textarea, max_length=10000) 
    class Meta:
        model = Factuur
        fields = (
            'factuur_werkzaamheden', 'factuur_artikelen',
        )


class ArtikelForm(forms.ModelForm):
    nieuw_artikel_omschrijving = forms.CharField(widget=forms.Textarea, max_length=200)
    class Meta:
        model = NieuwArtikel
        fields = (
            'nieuw_artikel_naam', 'nieuw_artikel_prijs', 'nieuw_artikel_omschrijving'
        )


class UserRegistratie(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField(help_text="Alleen letters, nummers en @/./+/-/_ toegestaan.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserLogin(forms.Form):
    gebruikersnaam = forms.CharField(max_length=100)
    wachtwoord =  forms.CharField(widget=forms.PasswordInput)


class KlantZoek(forms.Form):
    klantnummer = forms.IntegerField()


class OpmerkingenForm(forms.Form):

    OPMERKING_TYPE_CHOICES = (
        ('informatie', 'informatie'),
        ('vraag', 'vraag'),
    )
    opmerkingen = forms.CharField(widget=forms.Textarea, max_length=500)
    opmerking_type = forms.ChoiceField(choices=OPMERKING_TYPE_CHOICES)
    user_list = forms.ChoiceField(choices=[(u.id, u.username) for u in User.objects.all()])

    def clean_opmerkingen(self):
        opmerkingen = self.cleaned_data.get('opmerkingen')
        if 'something' not in opmerkingen:
            raise forms.ValidationError('Something must be in opmerkingen field.')
        return opmerkingen


class TicketSearchForm(forms.Form):
    apparaat_merk = forms.CharField(max_length=50, required=False) 
    ticket_onderwerp = forms.CharField(max_length=50, required=False)
    ticket_body = forms.CharField(max_length=50, required=False)
    klant_achternaam = forms.CharField(max_length=50, required=False)


class KlantSearchForm(forms.Form):
    klant_voornaam = forms.CharField(max_length=50, required=False)
    klant_achternaam = forms.CharField(max_length=50, required=False)
    klant_postcode = forms.CharField(max_length=6, required=False, disabled=True, widget=forms.TextInput(attrs={'placeholder': 'Coming soon..'}))
    klant_woonplaats = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'placeholder': 'Coming soon..'}))


class AntwoordForm(forms.Form):
    antwoord_body = forms.CharField(max_length=500, widget=forms.Textarea)


class ArtikelBoolean(forms.Form):
    nieuw_artikel = forms.BooleanField(required=False)
