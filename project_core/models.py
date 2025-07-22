from django.db import models
from django.conf import settings


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
