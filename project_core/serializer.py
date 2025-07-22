from .models import Project, Contributor
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class ProjectSerializer(ModelSerializer):
    """
    Sérialise le modèle Project.

    - Inclut tous les champs du modèle
    - Le champ 'author' est en lecture seule (défini automatiquement
      à la création)
    """

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["author"]


class ContributorSerializer(ModelSerializer):
    """
    Sérialise les contributeurs d'un projet.

    - Inclut l'ID du contributeur ainsi que les IDs liés
      (utilisateur et projet)
    - Ajoute aussi des informations plus lisibles :
        * user_name : le nom d'utilisateur du contributeur
        * project_name : le nom du projet associé
    """

    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ["id", "user", "user_name", "project", "project_name"]

    def get_user_name(self, obj):
        return obj.user.username

    def get_project_name(self, obj):
        return obj.project.name
