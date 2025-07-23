from .models import CustomUser
from .serializer import CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


# A remettre lorsque j'aurai géré les JWT,
# je m'auto bloque pour les tests avec postman sinon
# permission_classes = [IsAuthenticated]


class CustomUserView(APIView):
    """
    Gère la liste et la création des utilisateurs CustomUser

    - GET : retourne la liste de tous les utilisateurs
    - POST : crée un nouvel utilisateur
    """

    def get(self, request: Request) -> Response:
        """
        Retourne la liste de tous les utilisateurs CustomUser

        Args:
            request (Request): Objet Request contenant les infos HTTP

        Returns:
        - 200 OK : liste des utilisateurs au format JSON
        """

        queryset = CustomUser.objects.all()
        serializer_custom_user = CustomUserSerializer(queryset, many=True)

        return Response(serializer_custom_user.data, status=200)

    def post(self, request: Request) -> Response:
        """
        Crée un nouvel utilisateur CustomUser.

        - 201 Created : si la création réussit, retourne l’utilisateur créé
                        en JSON
        - 400 Bad Request : si les données sont invalides
        """

        serializer_custom_user = CustomUserSerializer(data=request.data)

        if serializer_custom_user.is_valid():
            serializer_custom_user.save()
            return Response(serializer_custom_user.data, status=201)

        return Response(serializer_custom_user.errors, status=400)


class CustomUserDetailView(APIView):
    """
    Gère le détail, la mise à jour et la suppression d'un
    utilisateur CustomUser

    - GET : retourne les infos d'un utilisateur spécifique
    - PUT/PATCH : modifie les infos d'un utilisateur
    - DELETE : supprime un utilisateur
    """

    def get(self, request, user_id):
        """
        Récupère un utilisateur CustomUser.

        Args:
            request (Request): Objet Request
            user_id (int): Identifiant unique de l'utilisateur à supprimer

        - 200 OK : Retourne les informations de l'utilisateur au format JSON
        - 404 Not Found : si aucun utilisateur ne correspond à
                          l'identifiant fourni
        """

        selected_user = get_object_or_404(CustomUser, pk=user_id)

        serializer_custom_user = CustomUserSerializer(selected_user)
        return Response(serializer_custom_user.data)

    def patch(self, request, user_id):
        """
        Modifie partiellement un utilisateur CustomUser.

        Args:
            request (Request): Objet Request
            user_id (int): Identifiant unique de l'utilisateur à supprimer

        - 200 OK : Retourne les informations de l'utilisateur au format JSON
        - 400 Bas Request : Erreurs de validation des données fournies
        - 404 Not Found : si aucun utilisateur ne correspond à
                          l'identifiant fourni
        """
        selected_user = get_object_or_404(CustomUser, pk=user_id)
        serializer_custom_user = CustomUserSerializer(
            selected_user, data=request.data, partial=True
        )

        if serializer_custom_user.is_valid():
            serializer_custom_user.save()
            return Response(serializer_custom_user.data, status=200)
        else:
            return Response(serializer_custom_user.errors, status=400)

    def put(self, request, user_id):
        """
        Modifie complètement un utilisateur CustomUser.
        Toutes les données obligatoires doivent être fournies.

        Args:
            request (Request): Objet Request
            user_id (int): Identifiant unique de l'utilisateur à supprimer

        - 200 OK : Retourne les informations de l'utilisateur au format JSON
        - 400 Bad Request : Erreurs de validation des données fournies
        - 404 Not Found : si aucun utilisateur ne correspond à
                          l'identifiant fourni
        """
        selected_user = get_object_or_404(CustomUser, pk=user_id)
        serializer_custom_user = CustomUserSerializer(
            selected_user,
            data=request.data
        )

        if serializer_custom_user.is_valid():
            serializer_custom_user.save()
            return Response(serializer_custom_user.data, status=200)
        else:
            return Response(serializer_custom_user.errors, status=400)

    def delete(self, request, user_id):
        """
        Supprime un utilisateur CustomUser

        Args:
            request (Request): Objet Request contenant les informations HTTP
                               de la requête
            user_id (int): Identifiant unique de l'utilisateur à supprimer

        Returns:
            Response:
                _ 204 No Content : Suppression réussie
                - 404 Not Found : Si aucun utilisateur ne correspond à
                                  l'identifiant fourni
        """
        selected_user = get_object_or_404(CustomUser, pk=user_id)

        selected_user.delete()
        return Response(status=204)
