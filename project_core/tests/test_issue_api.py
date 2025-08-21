from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from project_core.models import Project, Contributor, Issue
from datetime import date
from authentication.models import CustomUser


class TestIssueAPI(APITestCase):

    """
    Classe de tests pour les endpoints Issue

    Elle teste les différentes opérations CRUD pour les issues liées
    à un projet,
    en simulant différents types d'utilisateurs et en vérifiant les
    codes HTTP attendus
    """

    def setUp(self):
        """
        Prépare les données initiales avant chaque test

        - Crée un utilisateur authentifié
        - Crée un projet dont cet utilisateur est l'auteur
        - Ajoute cet utilisateur comme contributeur du projet
        - Crée une issue associée au projet avec cet utilisateur comme auteur
          et assigné
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

    # TESTS GET LISTE ISSUES
    def test_list_issues_as_authenticated_user(self):
        """
        Teste que l'utilisateur authentifié peut récupérer la liste des issues
        pour un projet donné

        - Envoie une requête GET sur /api/projects/<project_id>/issues/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que le titre de l'issue créée figure bien dans la réponse
        """
        url = reverse("issue-list", args=[self.project.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [issue["title"] for issue in response.json()["results"]]
        self.assertIn(self.issue.title, titles)

    def test_list_issues_as_anonymous_user(self):
        """
        Teste qu'un utilisateur non connecté ne peut pas accéder
        à la liste des issues d'un projet

        - Déconnecte l'utilisateur (pas d'authentification)
        - Envoie une requête GET sur /api/projects/<project_id>/issues/
        - Vérifie que le code HTTP est 401 Unauthorized
        """
        self.client.force_authenticate(user=None)
        url = reverse("issue-list", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TESTS GET DETAIL ISSUES
    def test_detail_issue_as_contributor(self):
        """
        Teste qu'un contributeur au projet peut voir le détail d'une issue

        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que le titre de l'issue retourné correspond bien à l'issue
        testée
        """
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.issue.title)

    def test_detail_issue_as_non_contributor(self):
        """
        Teste qu'un utilisateur qui n'est pas contributeur ne peut pas accéder
        au détail d'une issue

        - Crée un autre utilisateur non contributeur
        - Authentifie cet utilisateur
        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/<issue_id>/
        - Vérifie que le code HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="noncontrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_issue_not_found(self):
        """
        Teste la réponse quand l'issue demandée n'existe pas

        - Envoie une requête GET sur
          /api/projects/<project_id>/issues/999/ (id inexistant)
        - Vérifie que le code HTTP est 404 Not Found
        """
        id_issue = 999
        url = reverse("issue-detail", args=[self.project.id, id_issue])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TESTS CREATE ISSUES
    def test_create_issue_as_authenticated_user(self):
        """
        Teste qu'un utilisateur connecté peut créer une nouvelle issue
        sur un projet donné

        - Prépare des données valides pour créer une issue
        - Envoie une requête POST sur /api/projects/<project_id>/issues/ avec
          ces données
        - Vérifie que le code HTTP est 201 Created
        - Vérifie que le titre de l'issue retourné correspond aux données
          envoyées
        """
        data = {
            "title": "Issue test",
            "description": "Description de l'issue",
            "status": "to_do",
            "priority": "medium",
            "tag": "feature",
            "assignee": self.user.id
        }
        url = reverse("issue-list", args=[self.project.id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["author"], self.user.id)

    def test_create_issue_as_anonymous_user(self):
        """
        Teste qu'un utilisateur non connecté ne peut pas créer une issue

        - Déconnecte l'utilisateur (pas d'authentification)
        - Envoie une requête POST sur /api/projects/<project_id>/issues/
          avec des données valides
        - Vérifie que le code HTTP est 401 Unauthorized
        """
        self.client.force_authenticate(user=None)
        data = {
            "title": "Issue test",
            "description": "Description de l'issue",
            "status": "to_do",
            "priority": "medium",
            "tag": "feature",
            "assignee": self.user.id
        }
        url = reverse("issue-list", args=[self.project.id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_issue_with_invalid_data(self):
        """
        Teste la création d'une issue avec des données invalides

        - Prépare des données invalides (exemple : statut non valide)
        - Envoie une requête POST sur /api/projects/<project_id>/issues/
          avec ces données
        - Vérifie que le code HTTP est 400 Bad Request
        - Vérifie que la réponse contient une erreur sur le champ concerné
        """
        data = {
            "title": "Issue test",
            "description": "Description de l'issue",
            "status": "invalid_status",
            "priority": "medium",
            "tag": "feature",
            "assignee": self.user.id
        }
        url = reverse("issue-list", args=[self.project.id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    # TESTS PUT ISSUES
    def test_update_issue_as_author(self):
        """
        Teste que l'auteur d'une issue peut la modifier complètement

        - Authentifie l'auteur de l'issue
        - Prépare des données valides pour la mise à jour
        - Envoie une requête PUT sur
          /api/projects/<project_id>/issues/<issue_id>/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que le titre de l'issue retourné correspond aux données
          mises à jour
        """
        data = {
            "title": "Issue modifiée",
            "description": "Description mise à jour",
            "status": "in_progress",
            "priority": "high",
            "tag": "bug",
            "assignee": self.user.id
        }
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])

    def test_update_issue_as_contributor(self):
        """
        Teste qu'un contributeur au projet qui n'est pas l'auteur de l'issue
        ne peut pas modifier cette issue

        - Crée un autre utilisateur contributeur mais non auteur de l'issue
        - Authentifie cet utilisateur
        - Envoie une requête PUT avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="contrib_non_auteur",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        Contributor.objects.create(user=other_user, project=self.project)
        self.client.force_authenticate(user=other_user)

        data = {
            "title": "Tentative modification",
            "description": "Description non autorisée",
            "status": "in_progress",
            "priority": "high",
            "tag": "bug",
            "assignee": self.user.id
        }
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_issue_as_non_contributor(self):
        """
        Teste qu'un utilisateur qui n'est pas contributeur du projet ne peut
        pas modifier une issue de ce projet

        - Crée un utilisateur non contributeur
        - Authentifie cet utilisateur
        - Envoie une requête PUT avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_contrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        data = {
            "title": "Tentative modification",
            "description": "Description non autorisée",
            "status": "in_progress",
            "priority": "high",
            "tag": "bug",
            "assignee": self.user.id
        }
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_issue_not_found(self):
        """
        Teste la réponse quand on tente de modifier une issue qui n'existe pas

        - Envoie une requête PUT sur
          /api/projects/<project_id>/issues/999/ (id inexistant)
        - Vérifie que le code HTTP est 404 Not Found
        """
        id_issue = 999
        data = {
            "title": "Modification",
            "description": "Description",
            "status": "in_progress",
            "priority": "high",
            "tag": "bug",
            "assignee": self.user.id
        }
        url = reverse("issue-detail", args=[self.project.id, id_issue])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TESTS PATCH ISSUES
    def test_patch_issue_as_author(self):
        """
        Teste que l'auteur d'une issue peut modifier partiellement cette issue

        - Authentifie l'auteur de l'issue
        - Prépare des données partielles valides pour la mise à jour
          (ex: changement de status)
        - Envoie une requête PATCH sur
          /api/projects/<project_id>/issues/<issue_id>/
        - Vérifie que le code HTTP est 200 OK
        - Vérifie que le champ modifié dans la réponse correspond à la
          nouvelle valeur
        """
        data = {
            "status": "in_progress"
        }
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], data["status"])

    def test_patch_issue_as_contributor(self):
        """
        Teste qu'un contributeur non auteur ne peut pas modifier partiellement
        une issue

        - Crée un contributeur autre que l'auteur
        - Authentifie ce contributeur
        - Envoie une requête PATCH avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="contrib_non_auteur",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        Contributor.objects.create(user=other_user, project=self.project)
        self.client.force_authenticate(user=other_user)

        data = {
            "status": "in_progress"
        }
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_issue_as_non_contributor(self):
        """
        Teste qu'un utilisateur non contributeur ne peut pas modifier
        partiellement une issue

        - Crée un utilisateur qui n'est pas contributeur
        - Authentifie cet utilisateur
        - Envoie une requête PATCH avec des données valides
        - Vérifie que le code HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_contrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        data = {
            "status": "in_progress"
        }
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_issue_not_found(self):
        """
        Teste la réponse quand on tente de modifier partiellement une issue
        qui n'existe pas

        - Envoie une requête PATCH sur
          /api/projects/<project_id>/issues/<id_issue>/ (id inexistant)
        - Vérifie que le code HTTP est 404 Not Found
        """
        id_issue = 999
        data = {
            "status": "in_progress"
        }
        url = reverse("issue-detail", args=[self.project.id, id_issue])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TESTS DELETE ISSUES
    def test_delete_issue_as_author(self):
        """
        Teste que l'auteur d'une issue peut la supprimer

        - Authentifie l'auteur de l'issue
        - Envoie une requête DELETE sur
          /api/projects/<project_id>/issues/<issue_id>/
        - Vérifie que le code HTTP est 204 No Content
        - Vérifie que l'issue n'existe plus en base de données
        """
        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Issue.objects.filter(id=self.issue.id).exists())

    def test_delete_issue_as_contributor(self):
        """
        Teste qu'un contributeur non auteur ne peut pas supprimer une issue

        - Crée un utilisateur contributeur mais non auteur
        - Authentifie ce contributeur
        - Envoie une requête DELETE sur l'issue
        - Vérifie que le code HTTP est 403 Forbidden
        - Vérifie que l'issue existe toujours en base
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="contrib_non_auteur",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        Contributor.objects.create(user=other_user, project=self.project)
        self.client.force_authenticate(user=other_user)

        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Issue.objects.filter(id=self.issue.id).exists())

    def test_delete_issue_as_non_contributor(self):
        """
        Teste qu'un utilisateur non contributeur ne peut pas supprimer
        une issue

        - Crée un utilisateur non contributeur
        - Authentifie cet utilisateur
        - Envoie une requête DELETE sur l'issue
        - Vérifie que le code HTTP est 403 Forbidden
        - Vérifie que l'issue existe toujours en base
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="non_contrib",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        url = reverse("issue-detail", args=[self.project.id, self.issue.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Issue.objects.filter(id=self.issue.id).exists())

    def test_delete_issue_not_found(self):
        """
        Teste la suppression d'une issue inexistante

        - Envoie une requête DELETE sur
          /api/projects/<project_id>/issues/<id_issue>/ avec un id inexistant
        - Vérifie que le code HTTP est 404 Not Found
        """
        id_issue = 999
        url = reverse("issue-detail", args=[self.project.id, id_issue])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
