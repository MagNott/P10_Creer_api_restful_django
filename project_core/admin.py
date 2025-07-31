from django.contrib import admin
from project_core.models import Contributor, Project, Issue, Comment

# Register your models here.
admin.site.register(Project)
admin.site.register(Contributor)
admin.site.register(Issue)
admin.site.register(Comment)
