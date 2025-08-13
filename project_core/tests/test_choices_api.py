from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from authentication.models import CustomUser


class TestIssueProjectChoicesView(APITestCase):
    """
    Tests pour les endpoints 'choices' de l'API

    Ces tests vérifient :
    - Que les utilisateurs authentifiés peuvent récupérer correctement les
      listes de choix pour les champs des modèles 'Issue' et 'Project'
    - Que la structure de la réponse correspond au format attendu
      (clés et sous-clés)
    - Que les utilisateurs non authentifiés reçoivent un code 401 Unauthorized
    - Que les endpoints sont en lecture seule et refusent toute méthode
      d'écriture
    """
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="mdp123",
            date_birth="1990-01-01"
        )
        self.client.force_authenticate(self.user)

    def test_get_issue_choices_authenticated(self):
        """
        Vérifie que l'utilisateur authentifié peut accéder à l'endpoint
        IssueChoicesView

        - Un utilisateur connecté envoie une requête GET vers
          /api/issues/choices/
        - La réponse doit être 200 OK
        - Les clés 'status', 'priority' et 'tag' doivent être présentes
        - Chaque liste doit contenir des dictionnaires avec les clés
          'value' et 'label'
        """
        url = reverse("issue-choices") 
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("status", data)
        self.assertIn("priority", data)
        self.assertIn("tag", data)

        for item in data["status"]:
            self.assertIn("value", item)
            self.assertIn("label", item)

        for item in data["priority"]:
            self.assertIn("value", item)
            self.assertIn("label", item)

        for item in data["tag"]:
            self.assertIn("value", item)
            self.assertIn("label", item)

    def test_get_issue_choices_anonymous(self):
        """
        Vérifie qu'un utilisateur non authentifié ne peut pas accéder à
        IssueChoicesView

        - Un utilisateur anonyme envoie une requête GET vers
          /api/issues/choices/
        - La réponse doit être 401 Unauthorized
        """
        self.client.force_authenticate(user=None)
        url = reverse("issue-choices")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_choices_read_only(self):
        """
        Vérifie que l'endpoint IssueChoicesView est en lecture seule

        - Un utilisateur authentifié tente d'utiliser POST, PUT ou DELETE sur
          /api/issues/choices/
        - La réponse doit être 405 Method Not Allowed pour chacune de ces
          méthodes
        """
        url = reverse("issue-choices")
        self.assertEqual(
            self.client.post(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.put(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.delete(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TestProjectChoicesView(APITestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            username="testuser_project",
            password="mdp123",
            date_birth="1990-01-01"
        )

        self.client.force_authenticate(self.user)

    def test_get_project_choices_authenticated(self):
        """
        Vérifie que l'endpoint ProjectChoicesView est en lecture seule.

        - Un utilisateur authentifié tente d'utiliser POST, PUT ou DELETE sur
          /api/projects/choices/.
        - La réponse doit être 405 Method Not Allowed pour chacune de ces
          méthodes.
        """
        url = reverse("project-choices")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertIn("type", data)
        for item in data["type"]:
            self.assertIn("value", item)
            self.assertIn("label", item)

    def test_get_project_choices_anonymous(self):
        """
        Anonyme → 401.
        """
        url = reverse("project-choices")
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_project_choices_read_only(self):
        """
        Lecture seule → POST/PUT/DELETE interdits (405).
        """
        url = reverse("project-choices")
        self.assertEqual(
            self.client.post(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.put(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.delete(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
