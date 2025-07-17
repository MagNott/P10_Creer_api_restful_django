from django.urls import path
from .views import ProjectView
from .views import ProjectDetailView
from .views import ContributorView
from .views import ContributorDetailView


urlpatterns = [
    path('', ProjectView.as_view(), name='project-list-create'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/contributors/', ContributorView.as_view(), name='project-contributors'),
    path('<int:project_id>/contributors/<int:contributor_id>/', ContributorDetailView.as_view(), name='project-contributor-detail'),
]
