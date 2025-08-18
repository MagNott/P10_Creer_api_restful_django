from project_core.serializer import IssueSerializer
from project_core.models import Issue
from ..models import Project, Contributor
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..permissions import IsContributor, IsAuthor
from rest_framework.pagination import PageNumberPagination


class IssueView(APIView, PageNumberPagination):
    """
    Gère la liste et l'ajout des issues sur les projets sur l'URL :
    api/projects/id/issues

    - GET : Liste toutes les issues d'un projet où l'utilisateur authentifié
            est contributeur
    - POST : crée un nouveau une nouvelle issue sur un projet. L'auteur est
             défini automatiquement comme l'utilisateur ayant fait la requête.
    """

    def get(self, request: Request, project_id) -> Response:
        """
        Récupère la liste de toutes les issues d'un projet si l'utilisateur
        authentifié en est contributeur.

        Args:
            request (Request): Objet Request associé à l'utilisateur
            authentifié.
            project_id (int): Identifiant du projet ciblé.

        Returns:
            Response:
            - 200 OK avec une liste JSON des issues sérialisées.
            - 403 si l'utilisateur n'est pas contributeur du projet.
        """

        selected_project = get_object_or_404(Project, pk=project_id)

        if not Contributor.objects.filter(
            project=selected_project,
            user=request.user
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        issues = selected_project.issues.all().order_by("-created_time")

        paginated_issues = self.paginate_queryset(issues, request, view=self)

        issue_serializer = IssueSerializer(paginated_issues, many=True)

        return self.get_paginated_response(issue_serializer.data)

    def post(self, request: Request, project_id) -> Response:
        """
        Crée une nouvelle issue dans un projet si l'utilisateur authentifié
        est contributeur.

        - Le champ 'author' est automatiquement défini comme l'utilisateur.
        - Le champ 'project' est automatiquement défini depuis l'URL.

        Args:
            request (Request): Objet Request contenant les données JSON
            envoyées par l'utilisateur.
            project_id (int): Identifiant du projet ciblé.

        Returns:
            Response:
            - 201 Created avec les données de l'issue nouvellement créée.
            - 400 si les données envoyées ne sont pas valides.
            - 403 si l'utilisateur n'est pas contributeur du projet.
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        if not Contributor.objects.filter(
            project=selected_project,
            user=request.user
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        issue_serializer = IssueSerializer(data=request.data)

        if issue_serializer.is_valid():
            issue_serializer.save(
                project=selected_project,
                author=request.user
            )
            return Response(issue_serializer.data, status=201)
        else:
            return Response(issue_serializer.errors, status=400)


class IssueDetailView(APIView):
    """
    Gère l'affichage, la modification et la suppression d'une issue spécifique
    sur l'URL : api/projects/<project_id>/issues/<issue_id>/

    - GET : affiche les détails d'une issue si l'utilisateur est contributeur
            du projet.
    - (PUT/PATCH et DELETE seront ajoutés ensuite)
    """

    permission_classes = [IsContributor, IsAuthor]

    def get(self, request, project_id, issue_id):
        """
        Affiche les détails d'une issue spécifique si l'utilisateur est
        contributeur du projet.

        Args :
            request (Request) : requête HTTP envoyée par l'utilisateur.
            project_id (int) : identifiant du projet contenant l'issue.
            issue_id (int) : identifiant de l'issue ciblée.

        Returns :
            Response :
            - 200 OK avec les données de l'issue sérialisée.
            - 403 si l'utilisateur n'est pas contributeur du projet.
            - 404 si le projet ou l'issue n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        # if not Contributor.objects.filter(
        #     user=request.user, project=selected_project
        # ).exists():
        #     return Response({"detail": "Accès interdit"}, status=403)

        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        self.check_object_permissions(request, selected_issue)

        issue_serializer = IssueSerializer(selected_issue)

        return Response(issue_serializer.data, status=200)

    def delete(self, request, project_id, issue_id):
        """
        Supprime une issue spécifique d'un projet si l'utilisateur
        en est l'auteur.

        - Vérifie d'abord que l'utilisateur est contributeur du projet.
        - Vérifie ensuite qu'il est l'auteur de l'issue.
        - Supprime l'issue si les deux conditions sont remplies.

        Args:
            request (Request): Objet de la requête HTTP.
            project_id (int): Identifiant du projet ciblé.
            issue_id (int): Identifiant de l'issue à supprimer.

        Returns:
            Response:
            - 204 No Content si la suppression est effectuée avec succès.
            - 403 Forbidden si l'utilisateur n'est pas contributeur ou
              pas auteur.
            - 404 Not Found si le projet ou l'issue n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        # if not Contributor.objects.filter(
        #     user=request.user, project=selected_project
        # ).exists():
        #     return Response({"detail": "Accès interdit"}, status=403)

        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        self.check_object_permissions(request, selected_issue)

        # if not selected_issue.author == request.user:
        #     return Response({"detail": "Accès interdit"}, status=403)
        # else:
        selected_issue.delete()
        return Response(status=204)

    def patch(self, request, project_id, issue_id):
        """
        Modifie partiellement une issue existante, si l'utilisateur est à la
        fois contributeur du projet et auteur de l'issue.

        - L'issue est identifiée par `issue_id` et doit appartenir au projet
        identifié par `project_id`.

        Args:
            request (Request): Requête contenant les données de mise à jour.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue à modifier.

        Returns:
            Response:
            - 200 OK avec l'issue mise à jour si l'utilisateur est autorisé.
            - 400 si les données fournies sont invalides.
            - 403 si l'utilisateur n'a pas les droits requis.
            - 404 si le projet ou l'issue n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        # if not Contributor.objects.filter(
        #     user=request.user, project=selected_project
        # ).exists():
        #     return Response({"detail": "Accès interdit"}, status=403)

        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        self.check_object_permissions(request, selected_issue)

        # if not selected_issue.author == request.user:
        #     return Response({"detail": "Accès interdit"}, status=403)
        # else:
        issue_serializer = IssueSerializer(
            selected_issue,
            data=request.data,
            partial=True
        )
        if issue_serializer.is_valid():
            issue_serializer.save(
                author=request.user,
                project=selected_project
            )
            return Response(issue_serializer.data, status=200)

        return Response(issue_serializer.errors, status=400)

    def put(self, request, project_id, issue_id):
        """
        Modifie complètement une issue existante, si l'utilisateur est à la
        fois contributeur du projet et auteur de l'issue.

        - L'issue est identifiée par `issue_id` et doit appartenir au projet
        identifié par `project_id`.

        Args:
            request (Request): Requête contenant les données de mise à jour.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue à modifier.

        Returns:
            Response:
            - 200 OK avec l'issue mise à jour si l'utilisateur est autorisé.
            - 400 si les données fournies sont invalides.
            - 403 si l'utilisateur n'a pas les droits requis.
            - 404 si le projet ou l'issue n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)

        # if not Contributor.objects.filter(
        #     user=request.user, project=selected_project
        # ).exists():
        #     return Response({"detail": "Accès interdit"}, status=403)

        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        self.check_object_permissions(request, selected_issue)

        # if not selected_issue.author == request.user:
        #     return Response({"detail": "Accès interdit"}, status=403)
        # else:
        issue_serializer = IssueSerializer(
            selected_issue,
            data=request.data,
        )
        if issue_serializer.is_valid():
            issue_serializer.save(
                author=request.user,
                project=selected_project
        )
            return Response(issue_serializer.data, status=200)

        return Response(issue_serializer.errors, status=400)
