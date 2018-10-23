from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from datetime import timedelta, datetime
from functools import reduce

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, Http404, HttpResponse
from django.urls import reverse, reverse_lazy
from django.core import serializers
from django.contrib import messages
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
import json, operator

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Ticket, Klant, Opmerking, Notificatie, Apparaat, Factuur, NieuwArtikel
from .forms import TicketForm, KlantForm, ApparaatForm, UserLogin, UserRegistratie, KlantZoek, OpmerkingenForm, FactuurForm, TicketSearchForm, KlantSearchForm, AntwoordForm, ArtikelForm, ArtikelBoolean
from .utils import render_to_pdf
from django.contrib.auth.models import User, Group


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'tickets/index.html'
    context_object_name = 'openstaande_tickets'
    login_url = 'tickets:login'

    def get_context_data(self, **kwargs):
        threshold = timezone.now() - timedelta(days=7)
        context = super().get_context_data(**kwargs)
        context['totaal_klanten'] = len(Klant.objects.all())
        context['totaal_tickets'] = len(Ticket.objects.all())
        context['laatste_klanten'] = Klant.objects.order_by('-id')[:5]

        tijd_verstreken_tickets = Ticket.objects.filter(ticket_status="In behandeling").filter(ticket_datum_aangemaakt__lte=threshold)
        dagen = [(timezone.now() - ticket.ticket_datum_aangemaakt).days for ticket in tijd_verstreken_tickets]
        context['tijd_verstreken'] = list(zip(tijd_verstreken_tickets, dagen))

        context['title'] = 'Home'
        return context

    def get_queryset(self):
        tickets = Ticket.objects.filter(ticket_status="In behandeling").order_by('-ticket_datum_aangemaakt')
        dagen = [(timezone.now() - ticket.ticket_datum_aangemaakt).days for ticket in tickets]
        return list(zip(tickets, dagen))


class OverzichtViewKlant(LoginRequiredMixin, generic.ListView):
    search_form = KlantSearchForm
    template_name = 'tickets/overzicht_klant.html'
    login_url = 'tickets:login'

    def get(self, request):
        search_form = self.search_form(None)
        klant_list = Klant.objects.all()
        paginator = Paginator(klant_list, 20)

        page = request.GET.get('page')
        results = paginator.get_page(page)

        return render(request, self.template_name, {
                'search_form': search_form,
                'results': results,
                'title': 'Overzicht klanten'
            })

    def post(self, request):
        search_form = self.search_form(request.POST)
        if search_form.is_valid():
            filters = [
                ('klant_voornaam__contains', search_form.cleaned_data['klant_voornaam']),
                ('klant_achternaam__contains', search_form.cleaned_data['klant_achternaam']),
            ]

            q_list = [Q(x) for x in filters]
            results = Klant.objects.filter(reduce(operator.and_, q_list))

            return render(request, self.template_name, {
                'search_form': search_form,
                'results':results,
                'title': 'Overzicht klanten'
            })
        else:
            return redirect('tickets:overzicht_klant')


class OverzichtViewTicket(LoginRequiredMixin, generic.ListView):
    search_form = TicketSearchForm
    template_name = 'tickets/overzicht_ticket.html'
    login_url = 'tickets:login'

    def get(self, request):
        search_form = self.search_form(None)
        ticket_list = Ticket.objects.all()
        paginator = Paginator(ticket_list, 20)

        page = request.GET.get('page')
        results = paginator.get_page(page)

        return render(request, self.template_name, {
                'search_form': search_form,
                'results': results,
                'title': 'Overzicht tickets'
            })

    def post(self, request):
        search_form = self.search_form(request.POST)
        if search_form.is_valid():
            filters = [
                ('ticket_body__contains', search_form.cleaned_data['ticket_body']),
                ('ticket_onderwerp__contains', search_form.cleaned_data['ticket_onderwerp']),
                ('ticket_klant__klant_achternaam__contains', search_form.cleaned_data['klant_achternaam']),
                ('ticket_apparaat__apparaat_merk__contains', search_form.cleaned_data['apparaat_merk'])
            ]

            q_list = [Q(x) for x in filters]
            results = Ticket.objects.filter(reduce(operator.and_, q_list))

            return render(request, self.template_name, {
                'search_form': search_form,
                'results':results,
                'title': 'Overzicht tickets'
            })
        else:
            return redirect('tickets:overzicht_ticket')


class OverzichtViewTicketOpen(LoginRequiredMixin, generic.ListView):
    template_name = 'tickets/overzicht_open_ticket.html'
    context_object_name = 'tickets'
    login_url = 'tickets:login'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Alle openstaande tickets'
        return context

    def get_queryset(self):
        return Ticket.objects.filter(ticket_status="In behandeling")    


class OverzichtViewNotificatie(LoginRequiredMixin, generic.View):
    template_name = 'tickets/notificaties.html'
    login_url = 'tickets:login'

    def get(self, request):
        notificaties = Notificatie.objects.filter(notificatie_naar=request.user)
        return render(request, self.template_name, {
                'notificaties': notificaties,
                'title': "Alle notificaties",
            })


class DetailViewTicket(LoginRequiredMixin, generic.DetailView):
    model = Ticket
    form_class = OpmerkingenForm
    template_name = 'tickets/ticket.html'
    login_url = 'tickets:login'

    def get_succes_url(self, **kwargs):
        return reverse('tickets:detail', kwargs={"pk": self.kwargs['pk']})

    def get_object(self, **kwargs):
        return Ticket.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _ticket = self.get_object()
        form = self.form_class
        context['facturen'] = _ticket.get_facturen()
        context['tickets'] = _ticket.ticket_apparaat.get_tickets()
        context['title'] = 'Ticket'
        context['opmerkingen'] = _ticket.opmerking_set.all()
        context['form'] = form(None)
        context['antwoord_form'] = AntwoordForm
        return context


class DetailViewKlant(LoginRequiredMixin, generic.DetailView):
    model = Klant
    template_name = 'tickets/klant.html'
    login_url = 'tickets:login'

    def get_succes_url(self, **kwargs):
        return reverse('tickets:klant_detail', kwargs={"pk": self.kwargs['pk']})

    def get_object(self, **kwargs):
        return Klant.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        klant = self.get_object()
        tickets = klant.get_tickets()
        apparaten = klant.get_apparaten()

        context['title'] = 'Klant'
        context['tickets'] = tickets
        context['apparaten'] = apparaten
        return context


class KlantUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Klant
    login_url = 'tickets:login'
    fields = ['klant_voornaam', 'klant_achternaam', 'klant_telefoonnummer']
    template_name_suffix = '_update_form'
    success_message = 'Klant succesvol aangepast'

    def get_success_url(self, **kwargs):
        return reverse('tickets:klant_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.klant_aangepast_door = self.request.user
        form.instance.klant_datum_aangepast = timezone.now()
        return super(KlantUpdateView, self).form_valid(form)


class KlantCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Klant
    login_url = 'tickets:login'
    fields = ['klant_voornaam', 'klant_achternaam', 'klant_telefoonnummer', 'klant_emailadres']
    success_message = 'Klant succesvol aangemaakt'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boolean_form'] = ArtikelBoolean
        context['title'] = 'Nieuw Ticket | 1/3'
        return context


class KlantDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Klant
    success_url = reverse_lazy('tickets:index')
    template_name_suffix = "_check_delete"
    success_message = 'Klant met succes verwijderd'

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, self.success_message)
        return super(KlantDeleteView, self).delete(request, *args, **kwargs)


class ApparaatCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.View):
    apparaat_form = ApparaatForm
    template_name = 'tickets/apparaat_form.html'
    login_url = 'tickets:login'
    success_message = 'Apparaat succesvol aangemaakt'

    def get_object(self, **kwargs):
        return Klant.objects.get(pk=self.kwargs['pk'])

    def get(self, request, pk):
        try:
            klant = Klant.objects.get(pk=pk)
        except Klant.DoesNotExist:
            raise Http404('Klant bestaat niet.')
        apparaten = klant.apparaat_set.all()
        apparaat_form = self.apparaat_form(None)
        return render(request, self.template_name, {
                'apparaat_form': apparaat_form,
                'klant': klant,
                'apparaten': apparaten,
                'title': 'Nieuw Ticket | 2/3',
            })

    def post(self, request, pk):
        apparaat_form = self.apparaat_form(request.POST)
        if apparaat_form.is_valid():
            klant = Klant.objects.get(pk=pk)

            apparaat = klant.apparaat_set.create(
                apparaat_merk=apparaat_form.cleaned_data['apparaat_merk'],
                apparaat_type=apparaat_form.cleaned_data['apparaat_type'],
                apparaat_accessoires=apparaat_form.cleaned_data['apparaat_accessoires'],
                apparaat_staat=apparaat_form.cleaned_data['apparaat_staat'],
            )

            return redirect(reverse('tickets:klant_ticket', kwargs={"pk": apparaat.pk}))


class ApparaatUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Apparaat
    login_url = 'tickets:login'
    fields = ['apparaat_merk', 'apparaat_type', 'apparaat_accessoires', 'apparaat_staat']
    template_name_suffix = '_update_form'
    success_message = "Apparaat succesvol aangepast"


class ApparaatDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Apparaat
    success_url = reverse_lazy('tickets:index')
    template_name_suffix = "_check_delete"
    success_message = 'Apparaat met succes verwijderd'

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, self.success_message)
        return super(ApparaatDeleteView, self).delete(request, *args, **kwargs)


class ArtikelCreateView(LoginRequiredMixin, generic.View):
    artikel_form = ArtikelForm
    login_url = 'tickets:login'
    template_name = 'tickets/extra_artikel.html'

    def get(self, request, pk):
        artikel_form = self.artikel_form(None)
        factuur = Factuur.objects.get(pk=pk)
        return render(request, self.template_name, {
            'factuur': factuur,
            'form': artikel_form,
        })

    def post(self, request, pk):
        artikel_form = self.artikel_form(request.POST)
        factuur = Factuur.objects.get(pk=pk)
        return redirect(reverse('tickets:factuur_pdf', kwargs={'pk':factuur.id}))


class FactuurCreateView(LoginRequiredMixin, generic.View):
    factuur_form = FactuurForm
    artikel_bool = ArtikelBoolean
    login_url = 'tickets:login'
    template_name = 'tickets/factuur_form.html'

    def get(self, request, pk):
        factuur_form = self.factuur_form(None)
        artikel_bool = self.artikel_bool(None)
        ticket = Ticket.objects.get(pk=pk)

        if ticket.heeft_facturen():
            factuur = ticket.get_facturen()
        else:
            factuur = None

        return render(request, self.template_name, {
                'ticket': ticket,
                'factuur': factuur,
                'form': factuur_form,
                'artikel_bool': artikel_bool,
            })

    def post(self, request, pk):
        factuur_form = self.factuur_form(request.POST)
        artikel_bool = self.artikel_bool(request.POST)
        if factuur_form.is_valid():
            factuur = factuur_form.save(commit=False)
            ticket = Ticket.objects.get(pk=pk)
            factuur.factuur_ticket = ticket
            factuur.factuur_klant = ticket.ticket_klant
            factuur.factuur_datum_aangemaakt = timezone.now()
            factuur.factuur_aangemaakt_door = request.user
            factuur.save()
            factuur.factuur_artikelen.set(factuur_form.cleaned_data['factuur_artikelen'])
            if request.POST.get('nieuw_artikel'):
                return redirect(reverse('tickets:extra_artikel', kwargs={'pk': factuur.id}))
            return redirect(reverse('tickets:factuur_pdf', kwargs={'pk': factuur.id}))


class TicketKlantView(LoginRequiredMixin, SuccessMessageMixin, generic.View):
    ticket_form = TicketForm
    template_name = 'tickets/ticket_form.html'
    login_url = 'tickets:login'

    def get(self, request, pk):
        ticket_form = self.ticket_form(None)
        ticket_form.fields["ticket_prioriteit"].initial = ["normaal"]
        try:
            apparaat = Apparaat.objects.get(pk=pk)
        except Apparaat.DoesNotExist:
            raise Http404('Apparaat bestaat niet.')

        return render(request, self.template_name, {
                'ticket_form': ticket_form,
                'apparaat': apparaat,
                'title': 'Nieuw Ticket | 3/3'
            })

    def post(self, request, pk):
        ticket_form = self.ticket_form(request.POST)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            apparaat = Apparaat.objects.get(pk=pk)
            user = request.user
            ticket.ticket_onderwerp = ticket_form.cleaned_data['ticket_onderwerp']
            ticket.ticket_body = ticket_form.cleaned_data['ticket_body']
            ticket.ticket_datum_aangemaakt = timezone.now()
            ticket.ticket_auteur = user
            ticket.ticket_klant = apparaat.apparaat_klant
            ticket.ticket_apparaat = apparaat
            ticket.save()
            messages.add_message(request, messages.INFO, '/tickets/pdf/afhaalbewijs/ticket/%s/' % ticket.id)
            return redirect('tickets:index')


class TicketUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Ticket
    login_url = 'tickets:login'
    fields = ('ticket_onderwerp', 'ticket_body', 'ticket_prioriteit', 'ticket_status')
    template_name_suffix = '_update_form'
    success_message = 'Ticket succesvol aangepast'

    def form_valid(self, form):
        form.instance.ticket_auteur_bewerkt = self.request.user
        form.instance.ticket_datum_aangepast = timezone.now()
        form.instance.opmerking_set.create(
            opmerking_type="aangepast",
            opmerking_body="Ticket gegevens aangepast",
            opmerking_datum_aangemaakt=timezone.now(),
            opmerking_auteur=self.request.user
        )
        return super(TicketUpdateView, self).form_valid(form)


class TicketDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy('tickets:index')
    template_name_suffix = "_check_delete"
    success_message = 'Ticket met succes verwijderd'

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, self.success_message)
        return super(TicketDeleteView, self).delete(request, *args, **kwargs)


class OpmerkingDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Opmerking
    success_url = reverse_lazy('tickets:index')
    template_name_suffix = "_check_delete"
    success_message = 'Opmerking met succes verwijderd'

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, self.success_message)
        return super(OpmerkingDeleteView, self).delete(request, *args, **kwargs)


class UserLoginView(generic.View):
    form_class = UserLogin
    template_name = 'tickets/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form,
                                                    'title': 'Login'
                                                    })

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data['gebruikersnaam']
            password = form.cleaned_data['wachtwoord']

            user = authenticate(username=username.lower(), password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    messages.add_message(request, messages.SUCCESS, 'Welkom %s' % user.username.capitalize())
                    return redirect('tickets:index')
        messages.add_message(request, messages.ERROR, 'Gebruikersnaam of wachtwoord onjuist')
        return render(request, self.template_name, {'form': form,
                                                    'title': 'Login'
                                                    })


class GeneratePDF(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(pk=kwargs['pk'])
        context = {
            'klant_nummer': ticket.ticket_klant.id,
            'klant_voornaam': ticket.ticket_klant.klant_voornaam,
            'klant_achternaam': ticket.ticket_klant.klant_achternaam,
            'klant_telefoonnummer': ticket.ticket_klant.klant_telefoonnummer,
            'apparaat_merk': ticket.ticket_apparaat.apparaat_merk,
            'apparaat_type': ticket.ticket_apparaat.apparaat_type,
            'apparaat_accessoires': ticket.ticket_apparaat.apparaat_accessoires,
            'apparaat_staat': ticket.ticket_apparaat.apparaat_staat,
            'ticket_nummer': ticket.id,
            'ticket_onderwerp': ticket.ticket_onderwerp,
            'ticket_body': ticket.ticket_body,
        }
        pdf = render_to_pdf('afhaalbewijs.html', context)
        return HttpResponse(pdf, content_type='application/pdf')


class GenerateFactuur(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        factuur = Factuur.objects.get(pk=kwargs['pk'])
        context = {
            'ticket_nummer': factuur.factuur_ticket.id,
            'ticket_klacht': factuur.factuur_ticket.ticket_body,
            'klant_nummer': factuur.factuur_klant.id,
            'klant_voornaam': factuur.factuur_klant.klant_voornaam,
            'klant_achternaam': factuur.factuur_klant.klant_achternaam,
            'klant_telefoonnummer': factuur.factuur_klant.klant_telefoonnummer,
            'factuur_nummer': factuur.id,
            'factuur_datum_aangemaakt': factuur.factuur_datum_aangemaakt,
            'factuur_werkzaamheden': factuur.factuur_werkzaamheden,
            'factuur_artikelen': factuur.get_artikelen(),
            'factuur_extra_artikelen': factuur.get_extra_artikelen(),
            'factuur_totaal': factuur.get_totaal(),
            'datum': datetime.now().strftime("%m-%d-%Y"),
        }
        pdf = render_to_pdf('factuur.html', context)
        return HttpResponse(pdf, content_type='application/pdf')


@login_required
def ticket_afsluiten(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404("Ticket bestaat niet")

    if ticket.ticket_status == "Afgesloten":
        messages.add_message(request, messages.ERROR, 'Ticket is al afgesloten')
        return redirect(reverse('tickets:detail', kwargs={'pk': ticket.id}))
    
    elif not ticket.heeft_facturen():
        messages.add_message(request, messages.ERROR, 'Er is nog geen factuur gemaakt.')
        return redirect(reverse('tickets:maak_factuur', kwargs={'pk': ticket.id}))
    
    else:
        ticket.ticket_datum_verwijderd = timezone.now()
        ticket.ticket_status = "Afgesloten"
        ticket.save()
        if ticket.heeft_facturen():
            facturen = ticket.factuur_set.all()
        else:
            facturen = [""]
        ticket.opmerking_set.create(
            opmerking_type="afgesloten",
            opmerking_body="Ticket afgesloten. " + facturen[0].factuur_werkzaamheden,
            opmerking_datum_aangemaakt=timezone.now(),
            opmerking_auteur=request.user,
        )
        messages.add_message(request, messages.SUCCESS, 'Ticket afgesloten')
        return redirect(reverse('tickets:detail', kwargs={'pk': ticket.id}))


@login_required
def delete_notificatie(request, notificatie_id):
    try:
        notificatie = Notificatie.objects.get(pk=notificatie_id)
    except Notificatie.DoesNotExist:
        raise Http404("Notificatie bestaat niet")
    
    notificatie.delete()
    messages.add_message(request, messages.SUCCESS, 'Notificatie verwijderd')
    return redirect(reverse('tickets:overzicht_notificatie'))


@login_required
def plaats_antwoord(request, opmerking_id):
    try:
        opmerking = Opmerking.objects.get(pk=opmerking_id)
    except Opmerking.DoesNotExist:
        raise Http404("Opmerking bestaat niet")
    
    antwoord_body = request.POST.get('antwoord_body', None)

    antwoord = opmerking.antwoord_set.create(
        antwoord_body=antwoord_body,
        antwoord_datum_aangemaakt=timezone.now(),
        antwoord_auteur=request.user,
    )

    if request.user != opmerking.opmerking_auteur:
        antwoord.notificatie_set.create(
            notificatie_body=str(antwoord.antwoord_auteur).capitalize() + " heeft uw vraag beantwoord",
            notificatie_van=request.user,
            notificatie_naar = opmerking.opmerking_auteur,
            notificatie_datum_aangemaakt = timezone.now(),
        )
    return redirect(reverse('tickets:detail', kwargs={'pk': opmerking.opmerking_ticket.id}))


@login_required
def plaats_opmerking(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404("Ticket bestaat niet")

    try:
        opmerking_body = request.POST.get('opmerkingen', None)
        opmerking_type = request.POST.get('opmerking_type', None)
        opmerking = ticket.opmerking_set.create(
            opmerking_type=opmerking_type,
            opmerking_body=opmerking_body,
            opmerking_datum_aangemaakt=timezone.now(),
            opmerking_auteur=request.user,
        )

        if opmerking_type == "vraag":
            notificatie_naar = User.objects.get(pk=request.POST.get('user_list', None))
            opmerking.opmerking_ontvanger = notificatie_naar
            opmerking.save()
            opmerking.notificatie_set.create(
                notificatie_body=request.user.username.capitalize() + " heeft een vraag gesteld bij ticket IF" + str(ticket.id),
                notificatie_van=request.user,
                notificatie_naar = notificatie_naar,
                notificatie_datum_aangemaakt = timezone.now(),
            )

        messages.add_message(request, messages.SUCCESS, 'Opmerking succesvol geplaatst')
        return redirect(reverse('tickets:detail', kwargs={'pk':ticket_id}))

    except (KeyError, Opmerking.DoesNotExist):
        raise Http404("Er ging iets fout met het plaatsen van de opmerking")


@login_required
def ajax_artikel_toevoegen(request, factuur_id):
    try:
        factuur = Factuur.objects.get(pk=factuur_id)
    except Factuur.DoesNotExist:
        raise Http404("Factuur bestaat niet")

    try:
        artikel = factuur.nieuwartikel_set.create(
            nieuw_artikel_naam=request.POST.get('nieuw_artikel_naam', None),
            nieuw_artikel_prijs=request.POST.get('nieuw_artikel_prijs', None),
            nieuw_artikel_omschrijving=request.POST.get('nieuw_artikel_omschrijving', None),
            nieuw_artikel_toegev_door=request.user,
            nieuw_artikel_datum_toegev=timezone.now(),
        )

        data = {
            'status': 200,
            'message': 'OK',
            'factuur_id': factuur.id,
            'artikel_id': artikel.id,
            'artikel_naam': artikel.nieuw_artikel_naam,
            'artikel_prijs': artikel.nieuw_artikel_prijs,
            'artikel_omschrijving': artikel.nieuw_artikel_omschrijving,
        }
        return JsonResponse(data)

    except ValueError as e:
        return JsonResponse(
            {
                'message': 'Error',
                'error': str(e),
                'code': 300
            }
        )


@login_required
def ajax_artikel_verwijderen(request, artikel_id):
    try:
        artikel = NieuwArtikel.objects.get(pk=artikel_id)
    except NieuwArtikel.DoesNotExist:
        raise Http404("Artikel bestaat niet")

    try:
        artikel_id = artikel.id
        artikel.delete()

        data = {
            'artikel_id': artikel_id,
            'message': 'Artikel succesvol verwijderd',
            'code': 200,
        }
        return JsonResponse(data)
    except Exception as e:

        data = {
            'message': 'Error',
            'error': str(e),
            'code': 300,
        }
        return JsonResponse(data)


@login_required
def ajax_notificatie_gezien(request, notificatie_id):
    try:
        notificatie = Notificatie.objects.get(pk=notificatie_id)
    except Notificatie.DoesNotExist:
        raise Http404("Notificatie bestaat niet")

    notificatie.notificatie_gezien = True
    notificatie.save()
    
    data = {
        "message": "Notificatie gemarkeerd als gelezen",
        "code":200,
    }

    return JsonResponse(data)


@login_required
def ajax_get_klant(request):
    if request.method == 'POST':
        input_nummer = str(request.POST.get('input_nummer', None))
        filters = [
                ('klant_voornaam__startswith', input_nummer),
                ('klant_achternaam__startswith', input_nummer),
            ]
        q_list = [Q(x) for x in filters]
        results = Klant.objects.filter(reduce(operator.or_, q_list))[:5]
        if results and len(input_nummer) > 0:
            
            data = {
                'Message': 'Klant gegevens gevonden!',
                'Code': 2,
                'klant_array': [ {'klant_id':klant.id, 'klant_achternaam':klant.klant_achternaam, 'klant_voornaam':klant.klant_voornaam} for klant in results ]
            }
            return JsonResponse(data)
        
        else:
            data = {
            'Code': 3,
            'Message': "Geen klant gevonden",
            }
            return JsonResponse(data)
    else:
        data = {
                'Message': "Geen ajax request",
            }
        return JsonResponse(data)


@login_required
def ajax_add_device(request):

    if request.method == 'POST':
        print(type(request.POST.get('pk_ticket', None)))
        ticket = Ticket.objects.get(pk=request.POST.get('pk_ticket', None))
        apparaat = Apparaat(
            apparaat_merk=request.POST.get('apparaat_merk', None),
            apparaat_type=request.POST.get('apparaat_type', None),
            apparaat_accessoires=request.POST.get('apparaat_accessoires', None),
            apparaat_staat=request.POST.get('apparaat_staat', None),
            apparaat_klant=ticket.ticket_klant,
        )
        apparaat.save()
        ticket.ticket_apparaat = apparaat
        print(apparaat.id)

        try:
            ticket.save()
            return JsonResponse(
                {
                    'message': 'OK',
                    'code': 200,
                    'apparaat_merk':apparaat.apparaat_merk,
                    'apparaat_type':apparaat.apparaat_type,
                    'apparaat_accessoires':apparaat.apparaat_accessoires,
                    'apparaat_staat':apparaat.apparaat_staat,
                    'apparaat_pk':apparaat.id
                }
            )
        except ValueError as e:
            return JsonResponse(
                {
                    'message': 'Error',
                    'error': str(e),
                    'code': 300
                }
            )


@login_required
def loguit_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Succesvol uitgelogd')
    return redirect('tickets:login')
