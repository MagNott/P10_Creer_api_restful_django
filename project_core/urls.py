from django.urls import path
from .views.project_views import ProjectView
from .views.project_views import ProjectDetailView
from .views.contributor_views import ContributorView
from .views.contributor_views import ContributorDetailView


urlpatterns = [
    path("", ProjectView.as_view(), name="project-list-create"),
    path("<int:project_id>/",
         ProjectDetailView.as_view(),
         name="project-detail"),
    path(
        "<int:project_id>/contributors/",
        ContributorView.as_view(),
        name="project-contributors",
    ),
    path(
        "<int:project_id>/contributors/<int:contributor_id>/",
        ContributorDetailView.as_view(),
        name="project-contributor-detail",
    ),
]
