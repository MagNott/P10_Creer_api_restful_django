from django.shortcuts import render
from .models import Project, Contributor
from .serializer import ProjectSerializer, ContributorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import CustomUser as User


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


# Pour la route api/projects/id/contributeurs
class ContributorView(APIView):
    def get(self, request, project_id):
        selected_project = Project.objects.get(pk=project_id)

        if not Contributor.objects.filter(user=request.user, project=selected_project).exists():
            return Response({"detail": "Accès interdit"}, status=403)

        contributors_project = Contributor.objects.filter(project=selected_project)

        serializer_project = ContributorSerializer(contributors_project, many=True)

        return Response(serializer_project.data, status=200)

    def post(self, request, project_id):
        selected_project = Project.objects.get(pk=project_id)

        if request.user != selected_project.author:
            return Response({"detail": "Accès interdit"}, status=403)

        user_id = request.data.get('user')
        if not user_id:
            return Response({"detail": "ID utilisateur manquant"}, status=400)

        try:
            user_to_add = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable"}, status=404)

        if Contributor.objects.filter(project=selected_project, user=user_to_add).exists():
            return Response({"detail": "Déjà contributeur"}, status=400)

        contributor = Contributor.objects.create(project=selected_project, user=user_to_add)

        serializer = ContributorSerializer(contributor)

        return Response(serializer.data, status=201)


# Pour la route api/projects/id/contributeurs/id
class ContributorDetailView(APIView):
    def delete(self, request, project_id, contributor_id):
        selected_project = Project.objects.get(pk=project_id)

        if request.user != selected_project.author:
            return Response({"detail": "Accès interdit"}, status=403)

        try:
            selected_contributor = Contributor.objects.get(
                pk=contributor_id,
                project=selected_project
            )
        except Contributor.DoesNotExist:
            return Response({"detail": "Contributeur introuvable"}, status=404)

        if selected_contributor.user == selected_project.author:
            return Response({"detail": "Impossible de supprimer l'auteur du projet"}, status=400)

        selected_contributor.delete()
        return Response(status=204)
