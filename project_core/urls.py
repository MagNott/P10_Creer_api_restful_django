from django.urls import path
from .views import ProjectView
from .views import ProjectDetailView

urlpatterns = [
    path('', ProjectView.as_view(), name='project-list-create'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
]
