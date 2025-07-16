from django.shortcuts import render
from .models import Project, Contributor
from .serializer import ProjectSerializer, ContributorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


# Pour la route api/projects/
class ProjectView(APIView):

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


# Pour la route api/projects/id
class ProjectDetailView(APIView):

    def get(self, request, project_id):
        selected_project = Project.objects.get(pk=project_id)

        if not Contributor.objects.filter(user=request.user, project=selected_project).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        serializer = ProjectSerializer(selected_project)
        return Response(serializer.data)

    def delete(self, request, project_id):
        selected_project = Project.objects.get(pk=project_id)
        if selected_project.author == request.user:
            selected_project.delete()
            return Response(status=204)
        else:
            return Response({"detail": "Accès interdit"}, status=403)

    def patch(self, request, project_id):
        selected_project = Project.objects.get(pk=project_id)
        if selected_project.author == request.user:
            project_serializer = ProjectSerializer(selected_project, data=request.data, partial=True)
            if project_serializer.is_valid():
                project_serializer.save()
                return Response(project_serializer.data, status=200)
            else:
                return Response(project_serializer.errors, status=400)

    def put(self, request, project_id):
        selected_project = Project.objects.get(pk=project_id)
        if selected_project.author == request.user:
            project_serializer = ProjectSerializer(selected_project, data=request.data)
            if project_serializer.is_valid():
                project_serializer.save()
                return Response(project_serializer.data, status=200)
            else:
                return Response(project_serializer.errors, status=400)