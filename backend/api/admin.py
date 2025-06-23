from django.contrib import admin

from .models import Achievement, Certification, ContactMessage, Project, Publication, Resume, Tag, VisitorCount

admin.site.register(Project)
admin.site.register(Publication)
admin.site.register(Certification)
admin.site.register(Achievement)
admin.site.register(ContactMessage)
admin.site.register(Resume)
admin.site.register(Tag)


@admin.register(VisitorCount)
class VisitorCountAdmin(admin.ModelAdmin):
    list_display = ("count", "last_updated")

    # Prevent adding new counters or deleting the main one
    def has_add_permission(self, request):
        return False if VisitorCount.objects.exists() else True

    def has_delete_permission(self, request, obj=None):
        return False
