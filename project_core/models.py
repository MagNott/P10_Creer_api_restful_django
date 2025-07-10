from django.db import models
from django.conf import settings


class Project(models.Model):

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
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributions"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributors"
    )

    # contrainte pour éviter qu’un même utilisateur
    # soit plusieurs fois contributeur du même projet
    # cette contrainte aurait été gérée automatiquement par django si cela
    # avait été une table d'association simple
    class Meta:
        unique_together = ("user", "project")
