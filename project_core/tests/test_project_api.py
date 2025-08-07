from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from project_core.models import Project, Contributor
from datetime import date
from authentication.models import CustomUser


class TestProjectAPI(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="strongpassword",
            date_birth=date(2000, 1, 1)
        )
        self.client.force_authenticate(user=self.user)

        self.project = Project.objects.create(
            name="Projet Test",
            description="Projet de test",
            project_type="BACK_END",
            author=self.user,
        )
        Contributor.objects.create(user=self.user, project=self.project)

    def test_list_projects_as_authenticated_user(self):
        url = reverse("project-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Optionnel : vérifier que le projet est bien dans la réponse
        titles = [project["name"] for project in response.json()]
        self.assertIn(self.project.name, titles)
