from django.urls import path
from .views.project_views import ProjectView
from .views.project_views import ProjectDetailView
from .views.contributor_views import ContributorView
from .views.contributor_views import ContributorDetailView
from .views.issue_views import IssueView
from .views.issue_views import IssueDetailView
from .views.comment_views import CommentView
from .views.comment_views import CommentDetailView
from .views.choices_views import IssueChoicesView
from .views.choices_views import ProjectChoicesView

urlpatterns = [

    # Routes projets
    path("projects/", ProjectView.as_view(), name="project-list-create"),
    path(
        "projects/<int:project_id>/",
        ProjectDetailView.as_view(),
        name="project-detail"
    ),

    # Routes contributeurs
    path(
        "projects/<int:project_id>/contributors/",
        ContributorView.as_view(),
        name="project-contributors",
    ),
    path(
        "projects/<int:project_id>/contributors/<int:contributor_id>/",
        ContributorDetailView.as_view(),
        name="project-contributor-detail",
    ),

    # Routes issues
    path(
        "projects/<int:project_id>/issues/",
        IssueView.as_view(),
        name="issue-list"
    ),
    path(
        "projects/<int:project_id>/issues/<int:issue_id>/",
        IssueDetailView.as_view(),
        name="issue-detail"
    ),

    # Routes commentaires
    path(
        "projects/<int:project_id>/issues/<int:issue_id>/comments/",
        CommentView.as_view(),
        name="comment-list-create",
    ),
    path(
        "projects/<int:project_id>/issues/<int:issue_id>/comments/<uuid:comment_id>/",  # noqa: E501
        CommentDetailView.as_view(),
        name="comment-detail"
    ),

    # Routes choices globales
    path(
        'choices/issues/',
        IssueChoicesView.as_view(),
        name='issue-choices'
    ),
    path(
        'choices/projects/',
        ProjectChoicesView.as_view(),
        name='project-choices'
    ),
]
