from django.urls import path

from . import views


app_name = 'tickets'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('overzicht/tickets/', views.OverzichtViewTicket.as_view(), name='overzicht_ticket'),
    path('overzicht/tickets_open/', views.OverzichtViewTicketOpen.as_view(), name='overzicht_ticket_open'),
    path('overzicht/klanten/', views.OverzichtViewKlant.as_view(), name='overzicht_klant'),
    path('overzicht/notificaties/', views.OverzichtViewNotificatie.as_view(), name="overzicht_notificatie"),
    path('factuur/<int:pk>/extra_artikel/', views.ArtikelCreateView.as_view(), name="extra_artikel"),
    path('ticket/<int:pk>/', views.DetailViewTicket.as_view(), name='detail'),
    path('klant/<int:pk>/', views.DetailViewKlant.as_view(), name="klant_detail"),
    path('nieuw_ticket/klant/', views.KlantCreateView.as_view(), name="nieuw_klant"),
    path('<int:pk>/edit_klant/', views.KlantUpdateView.as_view(), name="edit_klant"),
    path('<int:pk>/delete_klant/', views.KlantDeleteView.as_view(), name="delete_klant"),
    path('nieuw_ticket/<int:pk>/apparaat/', views.ApparaatCreateView.as_view(), name="nieuw_apparaat"),
    path('<int:pk>/edit_apparaat/', views.ApparaatUpdateView.as_view(), name="edit_apparaat"),
    path('<int:pk>/delete_apparaat/', views.ApparaatDeleteView.as_view(), name="delete_apparaat"),
    path('<int:ticket_id>/plaats_opmerking/', views.plaats_opmerking, name="plaats_opmerking"),
    path('<int:pk>/delete_opmerking/', views.OpmerkingDeleteView.as_view(), name="delete_opmerking"),
    path('nieuw_ticket/<int:pk>/ticket/', views.TicketKlantView.as_view(), name="klant_ticket"),
    path('<int:pk>/edit_ticket/', views.TicketUpdateView.as_view(), name="edit_ticket"),
    path('<int:pk>/delete_ticket/', views.TicketDeleteView.as_view(), name="delete_ticket"),
    path('<int:ticket_id>/ticket_afsluiten/', views.ticket_afsluiten, name="ticket_afsluiten"),
    path('<int:notificatie_id>/delete_notificatie/', views.delete_notificatie, name="delete_notificatie"),
    path('<int:opmerking_id>/plaats_antwoord/', views.plaats_antwoord, name="plaats_antwoord"),
    path('ajax/zoek_klant/', views.ajax_get_klant, name="zoek_klant"),
    path('ajax/apparaat', views.ajax_add_device, name="ajax_apparaat"),
    path('ajax/artikel_toevoegen/<int:factuur_id>/', views.ajax_artikel_toevoegen, name="ajax_artikel_toevoegen"),
    path('ajax/artikel_verwijderen/<int:artikel_id>/', views.ajax_artikel_verwijderen, name="ajax_artikel_verwijderen"),
    path('ajax/notificatie_gezien/<int:notificatie_id>/', views.ajax_notificatie_gezien, name="notificatie_gezien"),
    path('pdf/afhaalbewijs/ticket/<int:pk>/', views.GeneratePDF.as_view(), name="afhaalbewijs_pdf"),
    path('pdf/factuur/<int:pk>/', views.GenerateFactuur.as_view(), name="factuur_pdf"),
    path('<int:pk>/factuur/', views.FactuurCreateView.as_view(), name="maak_factuur"),
    path('loguit/', views.loguit_view, name='loguit')
]
