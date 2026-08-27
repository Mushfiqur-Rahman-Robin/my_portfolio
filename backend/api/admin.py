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
    LLMCostTracking,
    PageVisit,
    Project,
    ProjectImage,
    Publication,
    Resume,
    Tag,
    TotalVisitorCount,
    VisitorAnalytics,
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


@admin.register(Publication)
class PublicationAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering_field_name = "display_order"
    list_display = ("title", "authors", "conference", "published_date", "display_order")
    list_filter = ("published_date", "conference")
    search_fields = ("title", "authors", "conference")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "authors",
                    "conference",
                    "publication_url",
                    "published_date",
                    "display_order",
                )
            },
        ),
    )


@admin.register(Certification)
class CertificationAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering_field_name = "display_order"
    list_display = ("name", "issuing_organization", "issue_date", "display_order")
    list_filter = ("issue_date", "issuing_organization")
    search_fields = ("name", "issuing_organization")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "issuing_organization",
                    "credential_url",
                    "issue_date",
                    "image",
                    "display_order",
                )
            },
        ),
    )


@admin.register(Achievement)
class AchievementAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering_field_name = "display_order"
    list_display = ("title", "date", "display_order")
    list_filter = ("date",)
    search_fields = ("title", "description")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "date",
                    "image",
                    "display_order",
                )
            },
        ),
    )


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


@admin.register(VisitorAnalytics)
class VisitorAnalyticsAdmin(admin.ModelAdmin):
    """Read-only admin view for visitor metadata analytics."""

    list_display = ("visited_at", "visitor_id", "ip_address", "country", "device_type")
    list_filter = ("country", "device_type", "visited_at")
    search_fields = ("visitor_id", "ip_address", "country", "user_agent")
    readonly_fields = ("id", "visitor_id", "ip_address", "country", "device_type", "user_agent", "visited_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    """Read-only admin view for per-page navigation logs."""

    list_display = ("visited_at", "page", "visitor_id")
    list_filter = ("visited_at",)
    search_fields = ("page", "visitor_id")
    readonly_fields = ("id", "visitor_id", "page", "visited_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LLMCostTracking)
class LLMCostTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "updated_at",
        "operation_type",
        "model_name",
        "session_total_tokens",
        "session_cost",
        "total_cost",
        "total_tokens",
        "job_or_session",
    )
    list_filter = ("operation_type", "model_name", "updated_at")
    search_fields = ("model_name", "job_name")
    readonly_fields = (
        "id",
        "session",
        "job_name",
        "operation_type",
        "model_name",
        "session_chat_tokens",
        "session_embedding_tokens",
        "session_total_tokens",
        "session_chat_cost",
        "session_embedding_cost",
        "session_cost",
        "total_chat_cost",
        "total_embedding_cost",
        "total_cost",
        "total_chat_tokens",
        "total_embedding_tokens",
        "total_tokens",
        "created_at",
        "updated_at",
    )
    ordering = ["-updated_at"]

    def job_or_session(self, obj):
        if obj.session:
            return f"Session: {str(obj.session.id)[:8]}"
        elif obj.job_name:
            return f"Job: {obj.job_name}"
        return "-"

    job_or_session.short_description = "Job/Session"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
