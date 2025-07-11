from .models import Project, Contributor
from rest_framework.serializers import ModelSerializer


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['author']


class ContributorSerializer(ModelSerializer):
    class Meta:
        model = Contributor
        fields = '__all__'

