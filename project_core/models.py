from django.db import models
from django.conf import settings
import uuid


class Project(models.Model):
    """
    Représente un projet géré dans l'application

        - created_time (DateTimeField) : date de création (auto)
        - author (ForeignKey) : utilisateur qui a créé le projet
        - name (CharField) : titre du projet
        - description (TextField) : résumé du projet
        - project_type (CharField) : catégorie (back-end, front-end, iOS...)
    """

    # Liste des catégories possibles pour un projet
    TYPE_CHOICES = [
        ("back-end", "Back-end"),
        ("front-end", "Front-end"),
        ("ios", "iOS"),
        ("android", "Android"),
    ]

    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_projects",
    )
    name = models.CharField(max_length=50)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=TYPE_CHOICES)


class Contributor(models.Model):
    """
    Représente un contributeur associé à un projet

        - created_time (DateTimeField) : date d'ajout du contributeur
                                         (automatique)
        - user (ForeignKey) : utilisateur qui est contributeur pour ce projet
        - project (ForeignKey) : projet auquel le contributeur est associé
    """

    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributions"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributors"
    )

    # Contrainte pour éviter qu’un même utilisateur soit ajouté plusieurs fois
    # au même projet. Si c'était une ManyToManyField simple,
    # Django la gérerait automatiquement.
    class Meta:
        unique_together = ("user", "project")


class Issue(models.Model):
    """
    Représente une issue (problème ou tâche) associée à un projet.

    Champs :
        - title (CharField) : titre court de l'issue.
        - description (TextField) : détails plus longs sur l'issue.
        - status (CharField, choices) : état actuel de l'issue
          (to_do, in_progress, finished).
        - priority (CharField, choices) : niveau d'importance
          (low, medium, high).
        - tag (CharField, choices) : type de l'issue (bug, feature, task).
        - project (ForeignKey) : projet auquel est rattachée l'issue.
        - author (ForeignKey) : utilisateur ayant créé l'issue.
        - assignee (ForeignKey) : utilisateur assigné à l'issue.
        - created_time (DateTimeField) : date de création,
          ajoutée automatiquement.
    """
    # Liste des statuts possibles pour une issue
    TYPE_STATUS = [
        ("to_do", "To DO"),
        ("in_progress", "In Progress"),
        ("finished", "Finished"),
    ]

    # Liste des priorités possibles pour une issue
    TYPE_PRIORITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    # Liste des tags possibles pour une issue
    TYPE_TAG = [
        ("bug", "Bug"),
        ("feature", "Feature"),
        ("task", "Task"),
    ]

    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_issues",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_issues",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues"
    )
    status = models.CharField(max_length=20, choices=TYPE_STATUS)
    priority = models.CharField(max_length=20, choices=TYPE_PRIORITY)
    tag = models.CharField(max_length=20, choices=TYPE_TAG)
    title = models.CharField(max_length=50)
    description = models.TextField()


class Comment(models.Model):
    """
    Représente un commentaire ajouté à une issue.

    Champs :
        - uuid (UUIDField) : identifiant unique généré automatiquement qui est
          paramétré comme étant la primary key.
        - description (TextField) : contenu du commentaire.
        - created_time (DateTimeField) : date de création automatique.
        - author (ForeignKey) : utilisateur qui a écrit le commentaire.
        - issue (ForeignKey) : issue associée au commentaire.
    """
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_comments",
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments"
        )
