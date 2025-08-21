from rest_framework.permissions import BasePermission
from .models import Project, Contributor, Issue, Comment


# PERMISSIONS CONCERNANT LES PROJETS
class IsContributor(BasePermission):
    """
    Vérifie si l'utilisateur est contributeur du projet concerné
    Fonctionne pour les objets de type Project, Issue ou Comment
    """

    message = "Vous devez être contributeur de ce projet pour y accéder."

    def has_object_permission(self, request, view, obj):
        """
        Vérifie que l'utilisateur authentifié est contributeur du projet
        concerné, en fonction de l'objet reçu.

        Le comportement s'adapte selon le type d'objet :
        - Si l'objet est un Project : vérifie la contribution directe.
        - Si l'objet est une Issue : vérifie la contribution au projet lié à
          l'issue.
        - Si l'objet est un Comment : vérifie la contribution au projet lié à
          l'issue du commentaire.

        Retourne :
            True si l'utilisateur est contributeur du projet associé,
            False sinon.
        """
        # Si pas d'utilisateur ou utilisateur non authentifié, on refuse direct
        if not request.user or not request.user.is_authenticated:
            return False

        # Si l'objet est un projet
        if isinstance(obj, Project):
            return Contributor.objects.filter(
                user=request.user,
                project=obj
            ).exists()

        # Si l'objet est une issue
        elif isinstance(obj, Issue):
            return Contributor.objects.filter(
                user=request.user,
                project=obj.project
            ).exists()

        # Si l'objet est un commentaire
        elif isinstance(obj, Comment):
            return Contributor.objects.filter(
                user=request.user,
                project=obj.issue.project
            ).exists()

        # Par défaut, refus
        return False


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
