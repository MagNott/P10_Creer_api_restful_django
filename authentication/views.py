from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import CustomUser
from .serializer import CustomUserSerializer


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
