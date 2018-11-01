from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('klant', views.KlantView)
router.register('apparaat', views.ApparaatView)
router.register('ticket', views.TicketView)
router.register('opmerking', views.OpmerkingView)
router.register('user', views.UserView)

urlpatterns = [
    path('', include(router.urls)),
]
