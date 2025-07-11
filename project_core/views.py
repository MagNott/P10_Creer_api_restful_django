from django.shortcuts import render
from .models import Project, Contributor
from .serializer import ProjectSerializer, ContributorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class ProjectView(APIView):
    model = Project
    serializer = ProjectSerializer

    def post(self, request):
        # 1. Sérialiser et valider les données entrantes
        serializer = ProjectSerializer(data=request.data)

        # 2. Si les données sont valides
        if serializer.is_valid():
            serializer.save(author=request.user)  # ← ici, on crée le projet
            return Response(serializer.data, status=201)

        # Sinon, on renvoie une erreur
        return Response(serializer.errors, status=400)
