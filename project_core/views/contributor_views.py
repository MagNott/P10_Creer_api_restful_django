from ..models import Project, Contributor
from ..serializer import ContributorSerializer
from rest_framework.views import APIView
from rest_framework.request import Request  # noqa: F401
from rest_framework.response import Response
from authentication.models import CustomUser as User
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


class ContributorView(APIView, PageNumberPagination):
    """
    Gère la liste et l'ajout des contributeurs sur l'URL :
    api/projects/<id>/contributeurs

    - GET : Retourne la liste des contributeurs du projet si l'utilisateur
            authentifié est contributeur de ce projet
    - POST : Ajoute un nouveau contributeur au projet
            (seul l'auteur du projet peut effectuer cette action)
    """

    def get(self, request, project_id):
        """
        Récupère la liste des contributeurs d'un projet donné
        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant unique du projet demandé

        Returns:
            Response:
                - 200 OK : Liste des contributeurs du projet au format JSON si
                           l'utilisateur est contributeur
                - 403 Forbidden : Accès refusé si l'utilisateur n'est pas
                                  contributeur du projet
                - 404 Not Found : Si le projet n'existe pas
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        if not Contributor.objects.filter(
            user=request.user, project=selected_project
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        contributors_project = Contributor.objects.filter(
            project=selected_project
        )

        paginated_contributors = self.paginate_queryset(
            contributors_project,
            request,
            view=self
        )

        serializer_project = ContributorSerializer(
            paginated_contributors,
            many=True
        )

        return self.get_paginated_response(serializer_project.data)

    def post(self, request, project_id):
        """
        Ajoute un nouveau contributeur à un projet donné (seul l'auteur du
        projet peut ajouter)

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant unique du projet demandé

        Returns:
            Response:
                - 201 Created : Contributeur ajouté avec ses informations au
                                format JSON
                - 400 Bad Request :
                                * ID utilisateur manquant dans la requête
                                * utilisateur déjà contributeur du projet
                - 403 Forbidden : Accès refusé si l'utilisateur n'est pas
                                  l'auteur du projet
                - 404 Not Found :
                                 * projet inexistant
                                 * utilisateur à ajouter introuvable
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        if request.user != selected_project.author:
            return Response({"detail": "Accès interdit"}, status=403)

        user_id = request.data.get("user")
        if not user_id:
            return Response({"detail": "ID utilisateur manquant"}, status=400)

        user_to_add = get_object_or_404(User, pk=user_id)

        if Contributor.objects.filter(
            project=selected_project, user=user_to_add
        ).exists():
            return Response({"detail": "Déjà contributeur"}, status=400)

        contributor = Contributor.objects.create(
            project=selected_project, user=user_to_add
        )

        serializer = ContributorSerializer(contributor)

        return Response(serializer.data, status=201)


class ContributorDetailView(APIView):
    """
    Gère la suppression d'un contributeur spécifique d'un projet via l'URL :
    api/projects/<project_id>/contributors/<contributor_id>/

    - DELETE : Supprime un contributeur du projet (seul l'auteur du projet
               peut effectuer cette action)
    """

    def delete(self, request, project_id, contributor_id):
        """
        Supprime un contributeur d'un projet donné (sauf l'auteur du projet).

        Args:
            request (Request): Objet Request associé à l'utilisateur
                               authentifié
            project_id (int): Identifiant unique du projet ciblé
            contributor_id (int): Identifiant unique du contributeur
                                  à supprimer

        Returns:
            Response:
                - 204 No Content : suppression réussie
                - 400 Bad Request : impossible de supprimer l'auteur du projet
                - 403 Forbidden : accès refusé si l'utilisateur connecté n'est
                                  pas l'auteur du projet
                - 404 Not Found :
                    * projet inexistant
                    * contributeur inexistant ou non lié à ce projet
        """

        selected_project = get_object_or_404(Project, pk=project_id)

        if request.user != selected_project.author:
            return Response({"detail": "Accès interdit"}, status=403)

        selected_contributor = get_object_or_404(
            Contributor, pk=contributor_id, project=selected_project
        )

        if selected_contributor.user == selected_project.author:
            return Response(
                {"detail": "Impossible de supprimer l'auteur du projet"},
                status=400
            )
        selected_contributor.delete()
        return Response(status=204)
