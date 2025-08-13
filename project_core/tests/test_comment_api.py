from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from project_core.models import Project, Contributor, Issue, Comment
from datetime import date
from authentication.models import CustomUser


class TestCommentAPI(APITestCase):

    """
    Classe de tests pour les endpoints Comment

    Elle teste les différentes opérations CRUD pour les commentaires liées
    à une issue, en simulant différents types d'utilisateurs et en vérifiant
    les codes HTTP attendus
    """

    def setUp(self):
        """
        Prépare les données initiales avant chaque test

        - Crée un utilisateur authentifié
        - Crée un projet dont cet utilisateur est l'auteur
        - Ajoute cet utilisateur comme contributeur du projet
        - Crée une issue associée au projet avec cet utilisateur comme auteur
          et assigné
        - Créé un commentaire associé à une issue avec cet utilisateur comme
          auteur et assigné
        """
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="strongpassword",
            date_birth=date(2000, 1, 1)
        )
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            name="Projet Test",
            description="Projet de test",
            project_type="back-end",
            author=self.user,
        )
        Contributor.objects.create(user=self.user, project=self.project)

        self.issue = Issue.objects.create(
            project=self.project,
            status="to_do",
            priority="medium",
            tag="feature",
            title="Nouvelle issue",
            description="Développer une nouvelle fonctionnalité",
            author=self.user,
            assignee=self.user,
        )

        self.comment = Comment.objects.create(
            issue=self.issue,
            description="Le commentaire d'une issue",
            author=self.user,
        )

    # TESTS LISTE COMMENTS
    def test_list_comments_as_authenticated_contributor(self):
        """
        Teste qu'un utilisateur connecté et contributeur du projet peut
        accéder à la liste des commentaires d'une issue

        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/comments/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que la liste retournée contient le commentaire créé dans
          le setup
        """
        url = reverse(
            "comment-list-create",
            args=[self.project.id, self.issue.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_comments_as_authenticated_non_contributor(self):
        """
        Teste qu'un utilisateur connecté mais non contributeur ne peut pas
        accéder à la liste des commentaires

        - Crée un utilisateur non contributeur
        - Authentifie ce nouvel utilisateur
        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/comments/
        - Vérifie que le code HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_contrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        url = reverse(
            "comment-list-create",
            args=[self.project.id, self.issue.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_comments_as_anonymous_user(self):
        """
        Teste qu'un utilisateur non connecté ne peut pas accéder à la liste
        des commentaires

        - Déconnecte l'utilisateur (force_authenticate None)
        - Envoie une requête GET sur 
          /api/projects/<project_id>/issues/<issue_id>/comments/
        - Vérifie que le code HTTP est 401 Unauthorized
        """
        self.client.force_authenticate(user=None)
        url = reverse(
            "comment-list-create",
            args=[self.project.id, self.issue.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TESTS CREATE COMMENTS
    def test_create_comment_as_authenticated_contributor(self):
        '''
        Teste qu'un utilisateur connecté et contributeur peut créer
        un commentaire

        - Prépare des données valides pour créer un commentaire
        - Envoie une requête POST sur
          /api/projects/<project_id>/issues/<issue_id>/comments/
        - Vérifie que le code HTTP est 201 Created
        - Vérifie que la description du commentaire retourné correspond aux
          données envoyées
        '''
        url = reverse(
            "comment-list-create",
            args=[self.project.id, self.issue.id]
        )
        data = {
            "description": "Nouveau commentaire de test"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["description"], data["description"])

    def test_create_comment_as_authenticated_non_contributor(self):
        '''
        Teste qu'un utilisateur connecté mais non contributeur ne peut pas
        créer un commentaire

        - Crée un utilisateur connecté qui n'est pas contributeur
        - Authentifie cet utilisateur
        - Envoie une requête POST avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_contrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        url = reverse(
            "comment-list-create",
            args=[self.project.id, self.issue.id]
        )
        data = {
            "description": "Nouveau commentaire de test"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment_as_anonymous_user(self):
        '''
        Teste qu'un utilisateur non connecté ne peut pas créer un commentaire

        - Déconnecte tout utilisateur (authentification à None)
        - Envoie une requête POST avec des données valides
        - Vérifie que le code HTTP est 401 Unauthorized
        '''
        self.client.force_authenticate(user=None)
        url = reverse(
            "comment-list-create",
            args=[self.project.id, self.issue.id]
        )
        data = {
            "description": "Nouveau commentaire de test"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_with_invalid_data(self):
        '''
        Teste la tentative de création d'un commentaire avec des données
        invalides

        - Prépare des données invalides (exemple : description vide)
        - Envoie une requête POST avec ces données
        - Vérifie que le code HTTP est 400 Bad Request
        - Vérifie que la réponse contient les erreurs attendues
        '''
        url = reverse(
                "comment-list-create",
                args=[self.project.id, self.issue.id]
        )
        data = {
            "description": ""
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TESTS GET DETAIL COMMENTS
    def test_detail_comment_as_authenticated_contributor(self):
        '''
        Teste qu'un utilisateur connecté et contributeur peut voir un
        commentaire spécifique

        - Authentifie un utilisateur contributeur
        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/comments/<comment_id>/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que la description du commentaire retourné correspond à
          celle attendue
        '''
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
            )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_comment_as_authenticated_non_contributor(self):
        '''
        Teste qu'un utilisateur connecté mais non contributeur ne peut pas voir
        un commentaire spécifique

        - Crée un utilisateur non contributeur
        - Authentifie cet utilisateur
        - Envoie une requête GET sur
        /api/projects/<project_id>/issues/<issue_id>/comments/<comment_id>/
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_contrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_comment_as_anonymous_user(self):
        '''
        Teste qu'un utilisateur non connecté ne peut pas voir un commentaire
        spécifique

        - Déconnecte tout utilisateur
        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/comments/<comment_id>/
        - Vérifie que le code HTTP est 401 Unauthorized
        '''
        self.client.force_authenticate(user=None)
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_comment_not_found(self):
        '''
        Teste qu'une requête sur un commentaire inexistant retourne
        404 Not Found

        - Authentifie un utilisateur valide
        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/comments/<comment_id_inexistant>/
        - Vérifie que le code HTTP est 404 Not Found
        '''
        id_comment = '12345678-1234-5678-1234-567812345678'  # UUID fictif
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, id_comment]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TESTS PUT DETAIL COMMENTS
    def test_update_comment_as_author(self):
        '''
        Teste qu'un auteur peut modifier complètement son commentaire

        - Authentifie l'auteur du commentaire
        - Prépare des données valides pour la mise à jour
        - Envoie une requête PUT sur
          /api/projects/<project_id>/issues/<issue_id>/comments/<comment_id>/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que les données mises à jour correspondent
        '''
        data = {
            "description": "Commentaire modifié complètement"
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], data["description"])

    def test_update_comment_as_non_author(self):
        '''
        Teste qu'un utilisateur non auteur ne peut pas modifier un commentaire

        - Crée et authentifie un utilisateur non auteur
        - Envoie une requête PUT avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_auteur",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        data = {
            "description": "Tentative de modification non autorisée"
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_not_found(self):
        '''
        Teste la mise à jour d'un commentaire inexistant

        - Envoie une requête PUT vers un commentaire ID inexistant
        - Vérifie que le code HTTP est 404 Not Found
        '''
        uuid_comment = "12345678-1234-5678-1234-567812345678"
        self.client.force_authenticate(user=self.user)
        data = {
            "description": "Modification sur commentaire inexistant"
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, uuid_comment]
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment_with_invalid_data(self):
        '''
        Teste la tentative de mise à jour avec des données invalides

        - Authentifie l'auteur du commentaire
        - Envoie une requête PUT avec des données invalides
          (ex : description vide)
        - Vérifie que le code HTTP est 400 Bad Request
        - Vérifie la présence d'erreurs dans la réponse
        '''
        data = {
            "description": ""
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    # TESTS PATCH DETAIL COMMENTS
    def test_patch_comment_as_author(self):
        '''
        Teste qu'un auteur peut modifier partiellement son commentaire

        - Authentifie l'auteur du commentaire
        - Envoie une requête PATCH avec des données valides partielles
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que les données modifiées correspondent
        '''
        data = {
            "description": "Modification partielle"
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], data["description"])

    def test_patch_comment_as_non_author(self):
        '''
        Teste qu'un utilisateur non auteur ne peut pas modifier partiellement
        un commentaire

        - Crée et authentifie un utilisateur non auteur
        - Envoie une requête PATCH avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_auteur_patch",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        data = {
            "description": "Modification partielle non autorisée"
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_comment_not_found(self):
        '''
        Teste la modification partielle d'un commentaire inexistant

        - Envoie une requête PATCH vers un commentaire ID inexistant
        - Vérifie que le code HTTP est 404 Not Found
        '''
        uuid_comment = "87654321-4321-6789-4321-678987654321"
        self.client.force_authenticate(user=self.user)
        data = {
            "description": "Patch sur commentaire inexistant"
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, uuid_comment]
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_comment_with_invalid_data(self):
        '''
        Teste la tentative de modification partielle avec des données invalides

        - Authentifie l'auteur du commentaire
        - Envoie une requête PATCH avec des données invalides
        (ex : description vide)
        - Vérifie que le code HTTP est 400 Bad Request
        - Vérifie la présence d'erreurs dans la réponse
        '''
        self.client.force_authenticate(user=self.user)
        data = {
            "description": ""
        }
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    # TESTS DELETE DETAIL COMMENTS
    def test_delete_comment_as_author(self):
        '''
        Teste que l'auteur peut supprimer son commentaire

        - Authentifie l'auteur du commentaire
        - Envoie une requête DELETE sur le commentaire
        - Vérifie que le code HTTP est 204 No Content
        - Vérifie que le commentaire n'existe plus en base
        '''
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(uuid=self.comment.uuid).exists())

    def test_delete_comment_as_non_author(self):
        '''
        Teste qu'un utilisateur non auteur ne peut pas supprimer un commentaire

        - Crée et authentifie un utilisateur non auteur
        - Envoie une requête DELETE sur le commentaire
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        other_user = CustomUser.objects.create_user(
            username="non_auteur_delete",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, self.comment.uuid]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_not_found(self):
        '''
        Teste la suppression d'un commentaire inexistant

        - Envoie une requête DELETE vers un commentaire ID inexistant
        - Vérifie que le code HTTP est 404 Not Found
        '''
        id_comment = "11223344-5566-7788-99aa-bbccddeeff00"
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "comment-detail",
            args=[self.project.id, self.issue.id, id_comment]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

