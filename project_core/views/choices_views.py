from rest_framework.views import APIView
from rest_framework.response import Response
from project_core.models import Project
from ..models import Issue
from rest_framework.request import Request


class IssueChoicesView (APIView):
    """
    Vue API permettant de récupérer toutes les valeurs possibles
    (choices) pour les champs status, priority et tag du modèle Issue.

    Cette vue est en lecture seule et ne répond qu'à la méthode GET.
    """
    def get(self, request: Request):
        """
        Gère la requête GET pour retourner les valeurs choices
        des champs status, priority et tag du modèle Issue.

        Retour :
            Un dictionnaire avec trois clés ("status", "priority", "tag"),
            chacune contenant une liste de dictionnaires
            {"value": ..., "label": ...}.
        """
        status_list = []

        for status_choice in Issue.TYPE_STATUS:
            status_dict = {
                "value": status_choice[0],
                "label": status_choice[1]
            }
            status_list.append(status_dict)

        priority_list = []

        for priority_choice in Issue.TYPE_PRIORITY:
            priority_dict = {
                "value": priority_choice[0],
                "label": priority_choice[1]
            }
            priority_list.append(priority_dict)

        tag_list = []

        for tag_choice in Issue.TYPE_TAG:
            tag_dict = {
                "value": tag_choice[0],
                "label": tag_choice[1]
            }
            tag_list.append(tag_dict)

        choices = {
            "status": status_list,
            "priority": priority_list,
            "tag": tag_list,
        }

        return Response(choices)


class ProjectChoicesView (APIView):
    """
    Vue API permettant de récupérer toutes les valeurs possibles
    (choices) pour le champ type du modèle Project.

    Cette vue est en lecture seule et ne répond qu'à la méthode GET.
    """
    def get(self, request: Request):
        """
        Gère la requête GET pour retourner les valeurs choices
        du champ type du modèle Project.

        Retour :
            Un dictionnaire avec une clé "type" contenant une liste
            de dictionnaires {"value": ..., "label": ...}
        """
        type_list = []

        for type_choice in Project.TYPE_CHOICES:
            type_dict = {
                "value": type_choice[0],
                "label": type_choice[1]
            }
            type_list.append(type_dict)

        return Response({"type": type_list})
