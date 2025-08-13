from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from project_core.models import Project, Contributor
from datetime import date
from authentication.models import CustomUser


class TestContributorAPI(APITestCase):
    """
    Tests essentiels pour les endpoints de gestion des contributeurs

    - Vérifie que seuls les contributeurs peuvent voir la liste des
      contributeurs
    - Vérifie que seul l'auteur peut ajouter un contributeur
    - Vérifie que seul l'auteur peut supprimer un contributeur (sauf lui-même)
    """

    def setUp(self):
        self.author = CustomUser.objects.create_user(
            username='author',
            password='pass123',
            date_birth=date(1990, 1, 1)
        )
        self.other_contributor = CustomUser.objects.create_user(
            username='other_contributor',
            password='pass123',
            date_birth=date(1992, 2, 2)
        )
        self.non_contrib_user = CustomUser.objects.create_user(
            username='noncontrib',
            password='pass123',
            date_birth=date(1995, 3, 3)
        )

        self.project = Project.objects.create(
            name='Projet Test',
            description='Test description',
            project_type='back-end',
            author=self.author,
        )
        Contributor.objects.create(user=self.author, project=self.project)
        Contributor.objects.create(
            user=self.other_contributor,
            project=self.project
        )

    # TESTS LIST CONTRIBUTEURS
    def test_list_contributors_as_authenticated_contributor(self):
        '''
        Teste qu'un utilisateur contributeur connecté peut accéder à la liste
        des contributeurs d'un projet

        - Authentifie un utilisateur contributeur
        - Envoie une requête GET sur /api/projects/<project_id>/contributors/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que la liste contient au moins un contributeur
        '''
        self.client.force_authenticate(user=self.other_contributor)
        url = reverse("project-contributors", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_contributors_as_authenticated_non_contributor(self):
        '''
        Teste qu'un utilisateur connecté mais non contributeur ne peut pas
        accéder à la liste des contributeurs

        - Crée un utilisateur non contributeur
        - Authentifie cet utilisateur
        - Envoie une requête GET sur /api/projects/<project_id>/contributors/
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        self.client.force_authenticate(user=self.non_contrib_user)
        url = reverse("project-contributors", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_contributors_as_anonymous_user(self):
        '''
        Teste qu'un utilisateur non connecté ne peut pas accéder à la liste
        des contributeurs

        - Déconnecte tout utilisateur (authentification None)
        - Envoie une requête GET sur /api/projects/<project_id>/contributors/
        - Vérifie que le code HTTP est 401 Unauthorized
        '''
        self.client.force_authenticate(user=None)
        url = reverse("project-contributors", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_contributor_as_author(self):
        '''
        Teste que l'auteur du projet peut ajouter un nouveau contributeur

        - Authentifie l'auteur du projet
        - Crée un utilisateur à ajouter
        - Envoie une requête POST sur /api/projects/<project_id>/contributors/
          avec l'ID utilisateur
        - Vérifie que le code HTTP est 201 Created
        - Vérifie que le contributeur ajouté est dans la réponse
        '''
        self.client.force_authenticate(user=self.author)
        new_user = CustomUser.objects.create_user(
            username="newcontrib",
            password="mdp123",
            date_birth=date(1995, 5, 5)
        )
        url = reverse("project-contributors", args=[self.project.id])
        data = {"user": new_user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], new_user.id)

    def test_add_contributor_as_non_author(self):
        '''
        Teste qu'un utilisateur non auteur ne peut pas ajouter un contributeur

        - Crée un utilisateur non auteur
        - Authentifie cet utilisateur
        - Envoie une requête POST sur /api/projects/<project_id>/contributors/
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="notauthor",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=self.non_contrib_user)
        url = reverse("project-contributors", args=[self.project.id])
        data = {"user": other_user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_contributor_with_missing_user_id(self):
        '''
        Teste la requête POST sans ID utilisateur

        - Authentifie l'auteur du projet
        - Envoie une requête POST sans champ "user"
        - Vérifie que le code HTTP est 400 Bad Request
        '''
        self.client.force_authenticate(user=self.author)
        url = reverse("project-contributors", args=[self.project.id])
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_contributor_already_exists(self):
        '''
        Teste l'ajout d'un utilisateur déjà contributeur

        - Authentifie l'auteur du projet
        - Envoie une requête POST avec un utilisateur déjà contributeur
        - Vérifie que le code HTTP est 400 Bad Request
        '''
        self.client.force_authenticate(user=self.author)
        url = reverse("project-contributors", args=[self.project.id])
        # user déjà contributeur (setup)
        data = {"user": self.other_contributor.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_contributor_with_nonexistent_user(self):
        '''
        Teste l'ajout d'un utilisateur inexistant

        - Authentifie l'auteur du projet
        - Envoie une requête POST avec un ID utilisateur invalide
        - Vérifie que le code HTTP est 404 Not Found
        '''
        self.client.force_authenticate(user=self.author)
        url = reverse("project-contributors", args=[self.project.id])
        data = {"user": 999}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_contributor_as_author(self):
        '''
        Teste que l'auteur du projet peut supprimer un contributeur

        - Authentifie l'auteur du projet
        - Crée un contributeur à supprimer
        - Envoie une requête DELETE sur
          /api/projects/<project_id>/contributors/<contributor_id>/
        - Vérifie que le code HTTP est 204 No Content
        - Vérifie que le contributeur n'existe plus en base
        '''
        self.client.force_authenticate(user=self.author)
        contrib_to_delete = Contributor.objects.create(
            user=CustomUser.objects.create_user(
                username="todelete",
                password="mdp123",
                date_birth=date(1988, 8, 8)
            ),
            project=self.project
        )
        url = reverse(
            "project-contributor-detail",
            args=[self.project.id, contrib_to_delete.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contributor.objects.filter(
            id=contrib_to_delete.id).exists()
        )

    def test_delete_contributor_as_non_author(self):
        '''
        Teste qu'un utilisateur non auteur ne peut pas supprimer un
        contributeur

        - Crée un utilisateur non auteur
        - Authentifie cet utilisateur
        - Crée un contributeur à supprimer
        - Envoie une requête DELETE sur
        /api/projects/<project_id>/contributors/<contributor_id>/
        - Vérifie que le code HTTP est 403 Forbidden
        '''
        self.client.force_authenticate(user=None)
        contrib_to_delete = Contributor.objects.create(
            user=CustomUser.objects.create_user(
                username="todelete2",
                password="mdp123",
                date_birth=date(1988, 8, 8)
            ),
            project=self.project
        )
        self.client.force_authenticate(user=self.other_contributor)
        url = reverse(
            "project-contributor-detail",
            args=[self.project.id, contrib_to_delete.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_contributor_author_cannot_be_deleted(self):
        '''
        Teste que l'auteur du projet ne peut pas être supprimé comme
        contributeur

        - Authentifie l'auteur du projet
        - Tente de supprimer l'auteur comme contributeur
        - Vérifie que le code HTTP est 400 Bad Request
        '''
        self.client.force_authenticate(user=self.author)
        url = reverse(
            "project-contributor-detail",
            args=[self.project.id, self.author.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_nonexistent_contributor(self):
        '''
        Teste la suppression d'un contributeur inexistant

        - Authentifie l'auteur du projet
        - Envoie une requête DELETE avec un contributeur_id invalide
        - Vérifie que le code HTTP est 404 Not Found
        '''
        self.client.force_authenticate(user=self.author)
        url = reverse(
            "project-contributor-detail",
            args=[self.project.id, 999]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


def test_delete_contributor_from_nonexistent_project(self):
    '''
    Teste la suppression d'un contributeur sur un projet inexistant

    - Authentifie l'auteur du projet
    - Envoie une requête DELETE avec un project_id invalide
    - Vérifie que le code HTTP est 404 Not Found
    '''
    self.client.force_authenticate(user=self.author)
    url = reverse("project-contributor-detail", args=[999, 1])
    response = self.client.delete(url)
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
