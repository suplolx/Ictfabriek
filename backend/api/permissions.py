from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    message = 'Je bent niet de eigenaar van deze ticket'
    
    def has_object_permission(self, request, view, obj):
        methods = ['GET']
        if request.method in methods:
            return True
        return obj.opmerking_auteur == request.user
    