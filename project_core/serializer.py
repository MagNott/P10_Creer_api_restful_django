from .models import Project, Contributor
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['author']


class ContributorSerializer(ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'user_name', 'project', 'project_name']

    def get_user_name(self, obj):
        return obj.user.username

    def get_project_name(self, obj):
        return obj.project.name
