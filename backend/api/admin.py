from django.contrib import admin

from .models import (
    Achievement,
    Certification,
    ContactMessage,
    Experience,
    ExperiencePhoto,
    Project,
    ProjectImage,
    Publication,
    Resume,
    Tag,
    VisitorCount,
)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1  # Number of empty forms to display


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "display_order", "is_featured", "created_at")
    list_filter = ("is_featured", "tags")
    search_fields = ("title", "description")
    inlines = [ProjectImageInline]  # Add inline for images
    filter_horizontal = ("tags",)  # Better many-to-many widget


# Inline for Experience photos
class ExperiencePhotoInline(admin.TabularInline):
    model = ExperiencePhoto
    extra = 1


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("company_name", "job_title", "start_date", "end_date", "is_current", "display_order")
    list_filter = ("is_current", "start_date", "end_date")
    search_fields = ("company_name", "work_details")
    inlines = [ExperiencePhotoInline]  # Add inline for photos
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "company_name",
                    "job_title",
                    ("start_date", "end_date", "is_current"),
                    "work_details",
                    "display_order",
                )
            },
        ),
    )


admin.site.register(Publication)
admin.site.register(Certification)
admin.site.register(Achievement)
admin.site.register(ContactMessage)
admin.site.register(Resume)
admin.site.register(Tag)


@admin.register(VisitorCount)
class VisitorCountAdmin(admin.ModelAdmin):
    list_display = ("count", "last_updated")

    def has_add_permission(self, request):
        return False if VisitorCount.objects.exists() else True

    def has_delete_permission(self, request, obj=None):
        return False
