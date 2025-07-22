from ..models import Project, Contributor
from ..serializer import ProjectSerializer
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class ProjectView(APIView):
    """
    Gère la liste et l'ajout des projets sur l'URL : api/projects/

    - GET : Liste tous les projets où l'utilisateur authentifié est
            contributeur
    - POST : crée un nouveau projet en définissant l'auteur comme l'utilisateur
             ayant fait la requête, et l'ajoute automatiquement comme
             contributeur
    """

    def post(self, request: Request) -> Response:
        """
        Permet de créer un nouveau projet et ajoute automatiquement
        l'utilisateur ayant fait la requête comme auteur et contributeur

        Args:
            request (Request): Objet Request contenant les données du projet
                               (title, description, type...).
        Returns:
            Response:
            - 201 Created avec les données du projet si la validation réussit
            - 400 Bad Request avec les erreurs de validation si la validation
              ne réussi pas
        """
        serializer_project = ProjectSerializer(data=request.data)

        if serializer_project.is_valid():
            new_project = serializer_project.save(author=request.user)
            Contributor.objects.create(user=request.user, project=new_project)
            return Response(serializer_project.data, status=201)

        return Response(serializer_project.errors, status=400)

    def get(self, request: Request) -> Response:
        """
        Récupère la liste de tous les projets où l'utilisateur authentifié est
        contributeur.

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.

        Returns:
            Response:
            - 200 OK avec une liste JSON de projets sérialisés où
              l'utilisateur est contributeur.
              Chaque projet contient les champs définis dans
              `ProjectSerializer`.
        """
        projects_contributor = Contributor.objects.filter(user=request.user)

        projects = []
        for project_contributor in projects_contributor:
            projects.append(project_contributor.project)

        serializer_project = ProjectSerializer(projects, many=True)

        return Response(serializer_project.data, status=200)


class ProjectDetailView(APIView):
    """
    Gère la consultation, la modification et la suppression d'un projet via
    l'URL : api/projects/<id>/
    - GET : Récupère les informations détaillées d'un projet si
            l'utilisateur est contributeur
    - DELETE : Supprime un projet si l'utilisateur est l'auteur
    - PATCH : Modifie partiellement un projet (titre, description, type) si
              l'utilisateur est l'auteur
    - PUT : Remplace complètement les informations d'un projet si
            l'utilisateur est l'auteur
    """

    def get(self, request, project_id):
        """
        Récupère le détail d'un projet si l'utilisateur est contributeur

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant unique du projet demandé

        Returns:
            Response:
                - 200 OK avec les données sérialisées du projet si
                  l'utilisateur est contributeur
                - 403 Forbidden si l'utilisateur n'est pas contributeur
                  du projet
                - 404 Not Found si le projet n'existe pas
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        if not Contributor.objects.filter(
            user=request.user, project=selected_project
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        serializer = ProjectSerializer(selected_project)
        return Response(serializer.data)

    def delete(self, request, project_id):
        """
        Supprime un projet uniquement si l'utilisateur authentifié en est
        l'auteur

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant unique du projet à supprimer

        Returns:
            Response:
                _ 204 no content : Suppression réussie si l'utilisateur est
                                   l'auteur du projet
                - 403 forbidden : Accès refusé si l'utilisateur n'est pas
                                  l'auteur du projet
                - 404 not found : Si aucun projet ne correspond à
                                  l'identifiant fourni
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        if selected_project.author == request.user:
            selected_project.delete()
            return Response(status=204)
        else:
            return Response({"detail": "Accès interdit"}, status=403)

    def patch(self, request, project_id):
        """
        Modifie partiellement un projet uniquement si l'utilisateur
        authentifié en est l'auteur

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant unique du projet à modifier

        Returns:
            Response:
                _ 200 OK : Modification réussie, retourne les nouvelles
                           données du projet
                - 400 Bad Request : Erreurs de validation des données fournies
                - 404 Not Found : Aucun projet ne correspond à l'identifiant
                                  fourni
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        if selected_project.author == request.user:
            project_serializer = ProjectSerializer(
                selected_project, data=request.data, partial=True
            )
            if project_serializer.is_valid():
                project_serializer.save()
                return Response(project_serializer.data, status=200)
            else:
                return Response(project_serializer.errors, status=400)

    def put(self, request, project_id):
        """
        Modifie complètement  un projet uniquement si l'utilisateur
        authentifié en est l'auteur

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant unique du projet à modifier

        Returns:
            Response:
                _ 200 OK : Modification réussie, retourne les nouvelles
                           données du projet
                - 400 Bad Request : Erreurs de validation des données fournies
                - 403 Forbidden : Accès refusé si l'utilisateur n'est pas
                                  l'auteur du projet
                - 404 Not Found : Aucun projet ne correspond à l'identifiant
                                  fourni
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        if selected_project.author != request.user:
            return Response({"détail": "Accès interdit"}, status=403)

        project_serializer = ProjectSerializer(
            selected_project,
            data=request.data
        )

        if project_serializer.is_valid():
            project_serializer.save()
            return Response(project_serializer.data, status=200)
        else:
            return Response(project_serializer.errors, status=400)
