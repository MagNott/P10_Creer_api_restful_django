from django.contrib import admin
from project_core.models import Contributor, Project

# Register your models here.
admin.site.register(Project)
admin.site.register(Contributor)
