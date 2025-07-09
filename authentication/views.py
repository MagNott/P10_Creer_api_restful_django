from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import CustomUser
from .serializer import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # A remettre lorsque j'aurai géré les JWT, je m'auto bloque pour les tests avec postman sinon
    # permission_classes = [IsAuthenticated]
