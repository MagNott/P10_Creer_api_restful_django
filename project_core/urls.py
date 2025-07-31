from django.urls import path
from .views.project_views import ProjectView
from .views.project_views import ProjectDetailView
from .views.contributor_views import ContributorView
from .views.contributor_views import ContributorDetailView
from .views.issue_views import IssueView
from .views.issue_views import IssueDetailView
from .views.comment_views import CommentView
from .views.comment_views import CommentDetailView

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
    path(
        "<int:project_id>/issues/",
        IssueView.as_view(),
        name="issue-list"
    ),
    path(
        "<int:project_id>/issues/<int:issue_id>/",
        IssueDetailView.as_view(),
        name="issue-detail"
    ),
    path(
        "<int:project_id>/issues/<int:issue_id>/comments/",
        CommentView.as_view(),
        name="comment-list-create",
    ),
    path(
        "<int:project_id>/issues/<int:issue_id>/comments/<uuid:comment_id>/",
        CommentDetailView.as_view(),
        name="comment-detail"
    ),
]
