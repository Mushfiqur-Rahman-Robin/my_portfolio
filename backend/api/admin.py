from django.contrib import admin

from .models import Achievement, Certification, Project, Publication

admin.site.register(Project)
admin.site.register(Publication)
admin.site.register(Certification)
admin.site.register(Achievement)
