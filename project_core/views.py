from .models import Project, Contributor
from .serializer import ProjectSerializer, ContributorSerializer
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from authentication.models import CustomUser as User
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


# Pour la route api/projects/id/contributeurs
class ContributorView(APIView):
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
        selected_project = Project.objects.get_object_or_404(pk=project_id)

        if not Contributor.objects.filter(
            user=request.user, project=selected_project
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        contributors_project = Contributor.objects.filter(
            project=selected_project
        )

        serializer_project = ContributorSerializer(
            contributors_project,
            many=True
        )

        return Response(serializer_project.data, status=200)

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


# Pour la route api/projects/id/contributeurs/id
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
