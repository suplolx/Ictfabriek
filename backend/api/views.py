from django.shortcuts import render
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from tickets.models import (
    Klant, Apparaat, Ticket, Opmerking
)
from django.contrib.auth.models import User
from .serializers import (
    KlantSerializer, UserSerializer, ApparaatSerializer, TicketSerializer, OpmerkingSerializer
)

from .permissions import IsOwnerOrReadOnly


class KlantView(viewsets.ModelViewSet):
    queryset = Klant.objects.all()
    serializer_class = KlantSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('klant_achternaam', 'klant_voornaam',)


class ApparaatView(viewsets.ModelViewSet):
    queryset = Apparaat.objects.all()
    serializer_class = ApparaatSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('apparaat_merk', 'apparaat_type',)


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


class TicketView(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('ticket_onderwerp',)


class OpmerkingView(viewsets.ModelViewSet):
    queryset = Opmerking.objects.all()
    serializer_class = OpmerkingSerializer
    permission_classes = (IsOwnerOrReadOnly,)
