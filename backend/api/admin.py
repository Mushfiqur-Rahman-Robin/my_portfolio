# backend/api/admin.py

from adminsortable2.admin import SortableAdminMixin
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms  # Import forms
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
class ProjectAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering_field_name = "display_order"
    list_display = ("title", "is_featured", "created_at")
    list_filter = ("is_featured", "tags")
    search_fields = ("title", "description")
    inlines = [ProjectImageInline]  # Add inline for images
    filter_horizontal = ("tags",)  # Better many-to-many widget


# Inline for Experience photos
class ExperiencePhotoInline(admin.TabularInline):
    model = ExperiencePhoto
    extra = 1


# Define a custom form for the Experience model to use CKEditor for work_details
class ExperienceAdminForm(forms.ModelForm):
    # This line tells Django's form to use the CKEditor widget for this field.
    # The underlying model field (models.TextField) remains unchanged.
    work_details = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Experience
        fields = "__all__"


@admin.register(Experience)
class ExperienceAdmin(SortableAdminMixin, admin.ModelAdmin):
    # Use the custom form
    form = ExperienceAdminForm

    ordering_field_name = "display_order"
    list_display = (
        "company_name",
        "job_title",
        "start_date",
        "end_date",
        "is_current",
    )
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
                    "work_details",  # This field will now display the CKEditor
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

    def has_add_permission(self, request):
        return False  # Prevent manual creation

    def has_change_permission(self, request, obj=None):
        return False  # Prevent manual editing

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion from the admin
