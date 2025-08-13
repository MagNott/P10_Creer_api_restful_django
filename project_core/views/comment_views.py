from project_core.models import Project, Contributor, Issue, Comment
from ..serializer import CommentSerializer
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..permissions import IsContributor, IsAuthor


class CommentView(APIView):
    """
    Gère les commentaires liés à une issue.

    - GET : Récupère tous les commentaires associés à une issue donnée
      (accessible uniquement aux contributeurs du projet).
    - POST : Permet de créer un commentaire sur une issue si l'utilisateur est
      contributeur du projet. L'auteur et l'issue sont attribués
      automatiquement.

    Routes concernées :
        - GET /api/projects/<project_id>/issues/<issue_id>/comments/
        - POST /api/projects/<project_id>/issues/<issue_id>/comments/
    """
    def get(self, request: Request, project_id, issue_id):
        """
        Récupère tous les commentaires associés à une issue spécifique,
        si l'utilisateur est contributeur du projet.

        - L'issue est identifiée par `issue_id` et doit appartenir au projet
          identifié par `project_id`.
        - L'utilisateur doit être contributeur du projet pour accéder aux
          commentaires.

        Args:
            request (Request): Requête HTTP reçue.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue concernée.

        Returns:
            Response:
            - 200 OK avec la liste des commentaires.
            - 403 si l'utilisateur n'est pas contributeur.
            - 404 si le projet ou l'issue n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )

        if not Contributor.objects.filter(
            project=selected_project,
            user=request.user
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        comments = selected_issue.comments.all()

        comment_serializer = CommentSerializer(comments, many=True)

        return Response(comment_serializer.data, status=200)

    def post(self, request: Request, project_id, issue_id):
        """
        Crée un nouveau commentaire sur une issue, si l'utilisateur est
        contributeur du projet.

        - Le commentaire est lié à l'issue et au projet donnés.
        - L'auteur du commentaire est défini automatiquement.
        - Le champ `description` doit être fourni dans la requête.

        Args:
            request (Request): Requête contenant les données du commentaire.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue concernée.

        Returns:
            Response:
            - 201 Created avec les données du commentaire.
            - 400 si les données sont invalides.
            - 403 si l'utilisateur n'est pas contributeur.
            - 404 si le projet ou l'issue n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )

        if not Contributor.objects.filter(
            project=selected_project,
            user=request.user
        ).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        comment_serializer = CommentSerializer(data=request.data)

        if comment_serializer.is_valid():
            comment_serializer.save(
                issue=selected_issue,
                author=request.user,
            )
            return Response(comment_serializer.data, status=201)
        else:
            return Response(comment_serializer.errors, status=400)


class CommentDetailView(APIView):
    """
    Gère les opérations sur un commentaire spécifique.

    Permet d'afficher, modifier ou supprimer un commentaire lié à une issue
    et à un projet donnés. Les règles d'autorisation sont les suivantes :
    - Tous les contributeurs peuvent consulter un commentaire.
    - Seul l'auteur du commentaire peut le modifier ou le supprimer.
    """

    permission_classes = [IsContributor, IsAuthor]

    def get(self, request: Request, project_id, issue_id, comment_id):
        """
        Récupère un commentaire spécifique si l'utilisateur est contributeur
        du projet.

        - Le commentaire est identifié par `comment_id`.
        - Il doit appartenir à l'issue `issue_id`, elle-même liée au projet
          `project_id`.

        Args:
            request (Request): Requête HTTP.
            project_id (int): Identifiant du projet.
            issue_id (int): Identifiant de l'issue.
            comment_id (UUID): Identifiant du commentaire.

        Returns:
            Response:
            - 200 avec les données du commentaire si l'accès est autorisé.
            - 403 si le commentaire ne correspond pas à l'issue ou au projet.
            - 404 si le projet, l'issue ou le commentaire (non lié à cette
                  issue) n'existent pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        selected_comment = get_object_or_404(
            Comment,
            pk=comment_id,
            issue=selected_issue
        )

        self.check_object_permissions(request, selected_comment)

        comment_serializer = CommentSerializer(selected_comment)

        return Response(comment_serializer.data, status=200)

    def delete(self, request, project_id, issue_id, comment_id):
        """
        Supprime un commentaire spécifique si l'utilisateur en est l'auteur
        et que le commentaire appartient bien à l'issue et au projet.

        Args:
            request (Request): La requête HTTP de suppression.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue concernée.
            comment_id (uuid): Identifiant unique du commentaire à supprimer.

        Returns:
            Response:
            - 204 No Content si la suppression a bien été effectuée.
            - 403 si l'utilisateur n'est pas l'auteur ou si les relations sont
                  invalides.
            - 404 si le projet, l'issue ou le commentaire n'existe pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        selected_comment = get_object_or_404(
            Comment,
            pk=comment_id,
            issue=selected_issue
        )

        self.check_object_permissions(request, selected_comment)

        # if not selected_comment.author == request.user:
        #     return Response({"detail": "Accès interdit"}, status=403)
        # else:
        selected_comment.delete()
        return Response(status=204)

    def patch(self, request, project_id, issue_id, comment_id):
        """
        Modifie partiellement un commentaire si l'utilisateur en est l'auteur
        et que le commentaire appartient bien à l'issue et au projet.

        Seul le champ `description` peut être modifié.

        Args:
            request (Request): Requête HTTP contenant les données à modifier.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue concernée.
            comment_id (uuid): Identifiant du commentaire à modifier.

        Returns:
            Response:
            - 200 OK avec les données mises à jour si l'utilisateur est
                  autorisé.
            - 400 si les données sont invalides.
            - 403 si l'utilisateur n'est pas l'auteur ou si les relations sont
              invalides.
            - 404 si le projet, l'issue ou le commentaire n'existent pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        selected_comment = get_object_or_404(
            Comment,
            pk=comment_id,
            issue=selected_issue
        )

        self.check_object_permissions(request, selected_comment)

        # if not selected_comment.author == request.user:
        #     return Response({"detail": "Accès interdit"}, status=403)
        # else:
        comment_serializer = CommentSerializer(
            selected_comment,
            data=request.data,
            partial=True
        )
        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data, status=200)

        return Response(comment_serializer.errors, status=400)

    def put(self, request, project_id, issue_id, comment_id):
        """
        Modifie complètement un commentaire si l'utilisateur en est l'auteur
        et que le commentaire appartient bien à l'issue et au projet.

        Seul le champ `description` est modifiable ; les autres champs comme
        `author` ou `issue` sont en lecture seule.

        Args:
            request (Request): Requête HTTP contenant les données à modifier.
            project_id (int): Identifiant du projet concerné.
            issue_id (int): Identifiant de l'issue concernée.
            comment_id (uuid): Identifiant du commentaire à modifier.

        Returns:
            Response:
            - 200 OK avec les données mises à jour si l'utilisateur est
                  autorisé.
            - 400 si les données sont invalides.
            - 403 si l'utilisateur n'est pas l'auteur ou si les relations sont
              invalides.
            - 404 si le projet, l'issue ou le commentaire n'existent pas.
        """
        selected_project = get_object_or_404(Project, pk=project_id)
        selected_issue = get_object_or_404(
            Issue,
            pk=issue_id,
            project=selected_project
        )
        selected_comment = get_object_or_404(
            Comment,
            pk=comment_id,
            issue=selected_issue
        )
        self.check_object_permissions(request, selected_comment)

        # if not selected_comment.author == request.user:
        #     return Response({"detail": "Accès interdit"}, status=403)
        # else:
        comment_serializer = CommentSerializer(
            selected_comment,
            data=request.data,
        )
        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data, status=200)

        return Response(comment_serializer.errors, status=400)
