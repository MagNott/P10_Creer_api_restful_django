from django.shortcuts import render
from .models import Project, Contributor
from .serializer import ProjectSerializer, ContributorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class ProjectView(APIView):
    model_project = Project
    serializer = ProjectSerializer

    def post(self, request):
        serializer_project = ProjectSerializer(data=request.data)

        if serializer_project.is_valid():
            new_project = serializer_project.save(author=request.user)
            Contributor.objects.create(user=request.user, project=new_project)
            return Response(serializer_project.data, status=201)

        return Response(serializer_project.errors, status=400)

    def get(self, request):
        projects_contributor = Contributor.objects.filter(user=request.user)

        projects = []
        for project_contributor in projects_contributor:
            projects.append(project_contributor.project)

        serializer_project = ProjectSerializer(projects, many=True)

        return Response(serializer_project.data, status=200)

