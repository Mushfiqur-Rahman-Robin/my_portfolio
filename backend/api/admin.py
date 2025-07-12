from django.contrib import admin

from .models import (
    Achievement,
    Certification,
    ChatMessage,
    ChatSession,
    ContactMessage,
    DailyVisitorCount,
    Experience,
    ExperiencePhoto,
    Project,
    ProjectImage,
    Publication,
    Resume,
    Tag,
    TotalVisitorCount,
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


class ChatMessageInline(admin.TabularInline):
    """Displays chat messages within the ChatSession view."""

    model = ChatMessage
    extra = 0  # Don't show any extra forms for new messages
    readonly_fields = ("sender", "message", "created_at")  # Make fields read-only
    can_delete = False  # Prevent deleting messages from the session view

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new messages from here


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin view for Chat Sessions."""

    list_display = ("id", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at")
    inlines = [ChatMessageInline]  # Nest the messages inside the session


admin.site.register(Publication)
admin.site.register(Certification)
admin.site.register(Achievement)
admin.site.register(ContactMessage)
admin.site.register(Resume)
admin.site.register(Tag)


@admin.register(TotalVisitorCount)
class TotalVisitorCountAdmin(admin.ModelAdmin):
    """Admin view for the single, cumulative visitor count."""

    list_display = ("count", "last_updated")
    readonly_fields = ("id", "last_updated", "count")

    def has_add_permission(self, request):
        return not TotalVisitorCount.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DailyVisitorCount)
class DailyVisitorCountAdmin(admin.ModelAdmin):
    """Admin view for daily visitor counts."""

    list_display = ("date", "count")
    list_filter = ("date",)
    readonly_fields = ("date", "count")
    ordering = ["-date"]

    # Allow viewing but prevent modifications
    def has_add_permission(self, request):
        return False  # Prevent manual creation

    def has_change_permission(self, request, obj=None):
        return False  # Prevent manual editing

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion from the admin

    # Override to ensure the changelist view works
    def changelist_view(self, request, extra_context=None):
        try:
            return super().changelist_view(request, extra_context)
        except Exception as e:
            # Log the error for debugging
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in DailyVisitorCount changelist: {e}", exc_info=True)

            # Return a basic response to prevent 500 error
            from django.contrib import messages

            messages.error(request, f"Error loading daily visitor counts: {e}")
            return super().changelist_view(request, extra_context)
