from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from project_core.models import Project, Contributor
from datetime import date
from authentication.models import CustomUser


class TestProjectAPI(APITestCase):
    """
    Classe de tests automatisés pour l'API Project

    Cette classe teste les différents endpoints liés aux projets,
    api/projects/ et api/projects/<id>/ notamment :
    - La liste des projets accessibles à un utilisateur authentifié ou non
    - La création de projet (validité des données, droits d'accès)
    - Le détail d'un projet (accès selon rôle contributeur ou non)
    - La mise à jour complète (PUT) des projets avec vérification des
      permissions
    - La mise à jour partielle (PATCH) des projets avec mêmes vérifications
    - Les cas d'erreur tels que projet non trouvé ou données invalides

    Chaque méthode teste un scénario spécifique, vérifiant le code HTTP renvoyé
    et le contenu de la réponse lorsque pertinent
    """

    def setUp(self):
        """
        Prépare les données initiales avant chaque test

        - Crée un utilisateur authentifié
        - Crée un projet dont cet utilisateur est l'auteur
        - Ajoute cet utilisateur comme contributeur du projet
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

    # TESTS GET LISTE PROJETS
    def test_list_projects_as_authenticated_user(self):
        """
        Teste que la récupération de la liste des projets par un utilisateur
        authentifié renvoie un statut 200 OK et inclut le projet créé

        - Envoie une requête GET sur /api/projects/
        - Vérifie que le statut HTTP est 200
        - Vérifie que le projet de test est bien dans la réponse JSON
        """
        url = reverse("project-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Optionnel : vérifier que le projet est bien dans la réponse
        titles = [project["name"] for project in response.json()]
        self.assertIn(self.project.name, titles)

    def test_list_projects_as_anonymous_user(self):
        """
        Teste que la récupération de la liste des projets par un utilisateur
        non authentifié renvoie un statut 401 Unauthorized

        - Désauthentifie le client
        - Envoie une requête GET sur /api/projects/
        - Vérifie que le statut HTTP est 401
        """
        self.client.force_authenticate(user=None)
        url = reverse("project-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TESTS CREATE PROJET
    def test_create_project_as_authenticated_user(self):
        """
        Teste la création d'un projet par un utilisateur authentifié

        - Envoie une requête POST avec des données valides
        - Vérifie que le statut HTTP est 201 Created
        - Vérifie que la réponse contient les données du projet créé
        """
        data = {
            "name": "Nouveau projet",
            "description": "Description du projet",
            "project_type": "back-end"
        }
        url = reverse("project-list-create")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])

    def test_create_project_as_anonymous_user(self):
        """
        Teste que la création d'un projet par un utilisateur non authentifié
        est interdite (401 Unauthorized)

        - Désauthentifie le client
        - Envoie une requête POST avec des données valides
        - Vérifie que le statut HTTP est 401
        """
        self.client.force_authenticate(user=None)
        data = {
            "name": "Nouveau projet",
            "description": "Description du projet",
            "project_type": "back-end"
        }
        url = reverse("project-list-create")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_with_invalid_data(self):
        """
        Teste que la création d'un projet avec des données invalides
        retourne une erreur 400 Bad Request

        - Envoie une requête POST avec des données incorrectes
        - Vérifie que le statut HTTP est 400
        - Vérifie que l'erreur concerne le champ 'project_type'
        """
        data = {
            "name": "Nouveau projet",
            "description": "Description du projet",
            "project_type": "BACK-END"
        }
        url = reverse("project-list-create")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project_type", response.data)

    # TESTS GET DETAIL PROJET
    def test_detail_project_as_contributor(self):
        """
        Teste que le contributeur d'un projet peut accéder au détail de
        celui-ci

        - Envoie une requête GET sur /api/projects/<id>/
        - Vérifie que le statut HTTP est 200 OK
        - Vérifie que les données retournées correspondent au projet
        """
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.project.name)

    def test_detail_project_as_non_contributor(self):
        """
        Teste que l'accès au détail d'un projet par un utilisateur non
        contributeur est interdit (403 Forbidden)

        - Authentifie un utilisateur non contributeur
        - Envoie une requête GET sur /api/projects/<id>/
        - Vérifie que le statut HTTP est 403
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="autre",
            password="mdp123",
            date_birth=date(1990, 1, 1))
        self.client.force_authenticate(user=other_user)

        url = reverse("project-detail", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_project_not_found(self):
        """
        Teste la gestion d'une requête GET pour un projet inexistant

        - Envoie une requête GET sur /api/projects/<id_inexistant>/
        - Vérifie que le statut HTTP est 404 Not Found
        """
        id_project = 999
        url = reverse("project-detail", args=[id_project])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TESTS PUT PROJET
    def test_update_project_as_author(self):
        """
        Teste que l'auteur d'un projet peut le modifier entièrement (PUT)

        - Envoie une requête PUT avec des données valides
        - Vérifie que le statut HTTP est 200 OK
        - Vérifie que les données retournées correspondent aux modifications
        """
        data = {
            "name": "Projet modifié",
            "description": "Description du projet",
            "project_type": "back-end"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], data["name"])

    def test_update_project_as_contributor(self):
        """
        Teste qu'un contributeur non auteur ne peut pas modifier un projet

        - Authentifie un utilisateur contributeur non auteur
        - Envoie une requête PUT
        - Vérifie que le statut HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="autre",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        data = {
            "name": "Projet modifié",
            "description": "Description du projet",
            "project_type": "back-end"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_as_non_contributor(self):
        """
        Teste qu'un utilisateur non contributeur ne peut pas modifier un
        projet

        - Authentifie un utilisateur non contributeur
        - Envoie une requête PUT
        - Vérifie que le statut HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="autre",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        data = {
            "name": "Projet modifié",
            "description": "Description du projet",
            "project_type": "back-end"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_not_found(self):
        """
        Teste la gestion d'une requête PUT sur un projet inexistant

        - Envoie une requête PUT sur /api/projects/<id_inexistant>/
        - Vérifie que le statut HTTP est 404 Not Found
        """
        id_project = 999
        url = reverse("project-detail", args=[id_project])
        data = {
            "name": "Projet modifié",
            "description": "Description du projet",
            "project_type": "back-end"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_project_with_invalid_data(self):
        """
        Teste la gestion d'une requête PUT avec des données invalides

        - Envoie une requête PUT avec données incorrectes
        - Vérifie que le statut HTTP est 400 Bad Request
        - Vérifie que l'erreur concerne le champ 'project_type'
        """
        data = {
            "name": "Nouveau projet",
            "description": "Description du projet",
            "project_type": "BACK-END"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project_type", response.data)

    # TESTS PATCH PROJET
    def test_patch_project_as_author(self):
        """
        Teste que l'auteur peut modifier partiellement un projet (PATCH)

        - Envoie une requête PATCH avec données partielles valides
        - Vérifie que le statut HTTP est 200 OK
        - Vérifie que la donnée modifiée est bien prise en compte
        """
        data = {
            "project_type": "back-end"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("project_type", response.data)
        self.assertEqual(response.data["project_type"], data["project_type"])

    def test_patch_project_as_contributor(self):
        """
        Teste qu'un contributeur non auteur ne peut pas modifier partiellement
        un projet

        - Authentifie un contributeur non auteur
        - Envoie une requête PATCH
        - Vérifie que le statut HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="autre",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )

        Contributor.objects.create(user=other_user, project=self.project)
        self.client.force_authenticate(user=other_user)

        data = {
            "project_type": "back-end"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_as_non_contributor(self):
        """
        Teste qu'un utilisateur non contributeur ne peut pas modifier
        partiellement un projet

        - Authentifie un utilisateur non contributeur
        - Envoie une requête PATCH
        - Vérifie que le statut HTTP est 403 Forbidden
        """
        self.client.force_authenticate(user=None)
        other_user = CustomUser.objects.create_user(
            username="autre",
            password="mdp123",
            date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        data = {
            "project_type": "back-end"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_project_not_found(self):
        """
        Teste la gestion d'une requête PATCH sur un projet inexistant

        - Envoie une requête PATCH sur /api/projects/<id_inexistant>/
        - Vérifie que le statut HTTP est 404 Not Found
        """
        id_project = 999
        url = reverse("project-detail", args=[id_project])
        data = {
            "project_type": "back-end"
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_with_invalid_data(self):
        """
        Teste la gestion d'une requête PATCH avec des données invalides

        - Envoie une requête PATCH avec données incorrectes
        - Vérifie que le statut HTTP est 400 Bad Request
        - Vérifie que l'erreur concerne le champ 'project_type'
        """
        data = {
            "name": "Nouveau projet",
            "description": "Description du projet",
            "project_type": "BACK-END"
        }
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project_type", response.data)

    # TEST DELETE
    def test_delete_project_as_author(self):
        """
        Teste que l'auteur d'un projet peut le supprimer

        - Authentifie l'utilisateur auteur
        - Envoie une requête DELETE sur /api/projects/<id>/
        - Vérifie que le statut HTTP est 204 No Content (suppression réussie)
        - Vérifie que le projet n'existe plus en base
        """
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_as_contributor(self):
        """
        Teste qu'un contributeur non-auteur ne peut pas supprimer un projet

        - Crée un autre utilisateur contributeur
        - Authentifie ce contributeur
        - Envoie une requête DELETE sur /api/projects/<id>/
        - Vérifie que le statut HTTP est 403 Forbidden
        - Vérifie que le projet existe toujours en base
        """
        other_user = CustomUser.objects.create_user(
            username="autre", password="mdp123", date_birth=date(1990, 1, 1)
        )
        Contributor.objects.create(user=other_user, project=self.project)
        self.client.force_authenticate(user=other_user)

        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_as_non_contributor(self):
        """
        Teste qu'un utilisateur non contributeur ne peut pas supprimer un
        projet

        - Crée un utilisateur non contributeur
        - Authentifie cet utilisateur
        - Envoie une requête DELETE sur /api/projects/<id>/
        - Vérifie que le statut HTTP est 403 Forbidden
        - Vérifie que le projet existe toujours en base
        """
        other_user = CustomUser.objects.create_user(
            username="autre", password="mdp123", date_birth=date(1990, 1, 1)
        )
        self.client.force_authenticate(user=other_user)

        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_not_found(self):
        """
        Teste la suppression d'un projet inexistant

        - Authentifie l'utilisateur auteur
        - Envoie une requête DELETE sur /api/projects/<id_inexistant>/
        - Vérifie que le statut HTTP est 404 Not Found
        """
        id_project = 999
        url = reverse("project-detail", args=[id_project])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
