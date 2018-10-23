from .models import Notificatie


def notifications(request):
    
    if request.user.is_authenticated:
        notifications = Notificatie.objects.filter(notificatie_naar=request.user).filter(notificatie_gezien=False)
        return {'notifications': notifications}
    
    else:
        return {}
