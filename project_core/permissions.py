from rest_framework.permissions import BasePermission
from .models import Contributor


class IsContributor(BasePermission):
    """
    La permission permet de vérifier que l'utilisateur authentifié
    est bien contributeur du projet concerné.
    """

    message = "Vous devez être contributeur de ce projet pour y accéder."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie que l'utilisateur (request.user) est contributeur
        du projet correspondant (obj).
        Retourne True si c'est le cas, False sinon.
        """
        return Contributor.objects.filter(
            user=request.user,
            project=obj
        ).exists()


class IsAuthor(BasePermission):
    """
    La permission permet de vérifier que l'utilisateur authentifié
    est bien auteur du projet concerné.
    """

    message = "Vous devez être auteur de ce projet pour réaliser cette action."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie que l'utilisateur (request.user) est auteur
        du projet correspondant (obj).
        Retourne True si c'est le cas, False sinon.
        """
        return obj.author == request.user
