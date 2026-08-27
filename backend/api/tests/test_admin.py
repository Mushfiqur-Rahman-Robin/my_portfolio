from io import BytesIO

from django.contrib.admin import AdminSite
from django.test import TestCase
from PIL import Image

from ..admin import (
    AchievementAdmin,
    CertificationAdmin,
    ChatMessageInline,
    ChatSessionAdmin,
    DailyVisitorCountAdmin,
    ExperienceAdmin,
    ExperiencePhotoInline,
    LLMCostTrackingAdmin,
    ProjectAdmin,
    ProjectImageInline,
    PublicationAdmin,
    TotalVisitorCountAdmin,
    VisitorAnalyticsAdmin,
)
from ..models import (
    Achievement,
    Certification,
    ChatMessage,
    ChatSession,
    ContactMessage,
    DailyVisitorCount,
    Experience,
    ExperiencePhoto,
    LLMCostTracking,
    Project,
    ProjectImage,
    Publication,
    Resume,
    Tag,
    TotalVisitorCount,
    VisitorAnalytics,
)


def _make_image():
    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, "png")
    buf.name = "test.png"
    buf.seek(0)
    return buf


class AdminRegistrationTests(TestCase):
    def test_project_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[Project], ProjectAdmin)

    def test_experience_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[Experience], ExperienceAdmin)

    def test_chat_session_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[ChatSession], ChatSessionAdmin)

    def test_publication_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[Publication], PublicationAdmin)

    def test_certification_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[Certification], CertificationAdmin)

    def test_achievement_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[Achievement], AchievementAdmin)

    def test_total_visitor_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[TotalVisitorCount], TotalVisitorCountAdmin)

    def test_daily_visitor_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[DailyVisitorCount], DailyVisitorCountAdmin)

    def test_visitor_analytics_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[VisitorAnalytics], VisitorAnalyticsAdmin)

    def test_llm_cost_tracking_admin_registered(self):
        from django.contrib import admin

        self.assertIsInstance(admin.site._registry[LLMCostTracking], LLMCostTrackingAdmin)

    def test_basic_registrations(self):
        from django.contrib import admin

        models = [ContactMessage, Resume, Tag]
        for model in models:
            self.assertIn(model, admin.site._registry)


class ProjectAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = ProjectAdmin(Project, self.site)
        self.image_data = _make_image()

    def test_list_display(self):
        self.assertEqual(self.model_admin.list_display, ("title", "is_featured", "created_at"))

    def test_list_filter(self):
        self.assertEqual(self.model_admin.list_filter, ("is_featured", "tags"))

    def test_search_fields(self):
        self.assertEqual(self.model_admin.search_fields, ("title", "description"))

    def test_inlines(self):
        self.assertEqual(self.model_admin.inlines, [ProjectImageInline])

    def test_filter_horizontal(self):
        self.assertEqual(self.model_admin.filter_horizontal, ("tags",))


class ProjectImageInlineTests(TestCase):
    def test_inline_model(self):
        inline = ProjectImageInline(Project, AdminSite())
        self.assertEqual(inline.model, ProjectImage)
        self.assertEqual(inline.extra, 1)


class ExperienceAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = ExperienceAdmin(Experience, self.site)

    def test_list_display(self):
        expected = ("company_name", "job_title", "start_date", "end_date", "is_current")
        self.assertEqual(self.model_admin.list_display, expected)

    def test_list_filter(self):
        self.assertEqual(self.model_admin.list_filter, ("is_current", "start_date", "end_date"))

    def test_search_fields(self):
        self.assertEqual(self.model_admin.search_fields, ("company_name", "work_details"))

    def test_inlines(self):
        self.assertEqual(self.model_admin.inlines, [ExperiencePhotoInline])

    def test_fieldsets_contains_work_details(self):
        flat_fields = []
        for _, opts in self.model_admin.fieldsets:
            flat_fields.extend(opts["fields"])
        self.assertIn("work_details", flat_fields)

    def test_form_uses_ckeditor_widget(self):
        from ckeditor_uploader.widgets import CKEditorUploadingWidget

        self.assertIsNotNone(self.model_admin.form)
        form = self.model_admin.form()
        widget = form.fields["work_details"].widget
        self.assertIsInstance(widget, CKEditorUploadingWidget)


class ExperiencePhotoInlineTests(TestCase):
    def test_inline_model(self):
        inline = ExperiencePhotoInline(Experience, AdminSite())
        self.assertEqual(inline.model, ExperiencePhoto)
        self.assertEqual(inline.extra, 1)


class ChatSessionAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = ChatSessionAdmin(ChatSession, self.site)

    def test_list_display(self):
        self.assertIn("id", self.model_admin.list_display)
        self.assertIn("created_at", self.model_admin.list_display)

    def test_inlines(self):
        self.assertEqual(self.model_admin.inlines, [ChatMessageInline])


class ChatMessageInlineTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.inline = ChatMessageInline(ChatSession, self.site)

    def test_model_and_extra(self):
        self.assertEqual(self.inline.model, ChatMessage)
        self.assertEqual(self.inline.extra, 0)

    def test_readonly_fields(self):
        self.assertEqual(self.inline.readonly_fields, ("sender", "message", "created_at"))

    def test_can_delete_false(self):
        self.assertFalse(self.inline.can_delete)

    def test_has_add_permission_false(self):
        request = type("Request", (), {"user": None})()
        self.assertFalse(self.inline.has_add_permission(request))


class PublicationAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = PublicationAdmin(Publication, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.model_admin.list_display,
            ("title", "authors", "conference", "published_date", "display_order"),
        )


class CertificationAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = CertificationAdmin(Certification, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.model_admin.list_display,
            ("name", "issuing_organization", "issue_date", "display_order"),
        )


class AchievementAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = AchievementAdmin(Achievement, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.model_admin.list_display,
            ("title", "date", "display_order"),
        )


class TotalVisitorCountAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = TotalVisitorCountAdmin(TotalVisitorCount, self.site)

    def test_list_display(self):
        self.assertEqual(self.model_admin.list_display, ("count", "last_updated"))

    def test_readonly_fields(self):
        self.assertIn("count", self.model_admin.readonly_fields)
        self.assertIn("last_updated", self.model_admin.readonly_fields)

    def test_has_add_permission_returns_true_when_no_records(self):
        request = type("Request", (), {"user": None})()
        self.assertTrue(self.model_admin.has_add_permission(request))

    def test_has_add_permission_returns_false_when_record_exists(self):
        TotalVisitorCount.objects.create(count=1)
        request = type("Request", (), {"user": None})()
        self.assertFalse(self.model_admin.has_add_permission(request))

    def test_has_delete_permission_returns_false(self):
        request = type("Request", (), {"user": None})()
        self.assertFalse(self.model_admin.has_delete_permission(request, obj=None))


class DailyVisitorCountAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = DailyVisitorCountAdmin(DailyVisitorCount, self.site)

    def test_list_display(self):
        self.assertEqual(self.model_admin.list_display, ("date", "count"))

    def test_readonly_fields(self):
        self.assertIn("date", self.model_admin.readonly_fields)
        self.assertIn("count", self.model_admin.readonly_fields)

    def test_permissions_return_false(self):
        request = type("Request", (), {"user": None})()
        self.assertFalse(self.model_admin.has_add_permission(request))
        self.assertFalse(self.model_admin.has_change_permission(request, obj=None))
        self.assertFalse(self.model_admin.has_delete_permission(request, obj=None))


class VisitorAnalyticsAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = VisitorAnalyticsAdmin(VisitorAnalytics, self.site)

    def test_list_display(self):
        expected = ("visited_at", "visitor_id", "ip_address", "country", "device_type")
        self.assertEqual(self.model_admin.list_display, expected)

    def test_list_filter(self):
        self.assertEqual(
            self.model_admin.list_filter,
            ("country", "device_type", "visited_at"),
        )

    def test_search_fields(self):
        self.assertEqual(
            self.model_admin.search_fields,
            ("visitor_id", "ip_address", "country", "user_agent"),
        )

    def test_permissions_return_false(self):
        request = type("Request", (), {"user": None})()
        self.assertFalse(self.model_admin.has_add_permission(request))
        self.assertFalse(self.model_admin.has_change_permission(request, obj=None))
        self.assertFalse(self.model_admin.has_delete_permission(request, obj=None))


class LLMCostTrackingAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.model_admin = LLMCostTrackingAdmin(LLMCostTracking, self.site)

    def test_list_display(self):
        expected = (
            "updated_at",
            "operation_type",
            "model_name",
            "session_total_tokens",
            "session_cost",
            "total_cost",
            "total_tokens",
            "job_or_session",
        )
        self.assertEqual(self.model_admin.list_display, expected)

    def test_ordering(self):
        self.assertEqual(self.model_admin.ordering, ["-updated_at"])

    def test_permissions_return_false(self):
        request = type("Request", (), {"user": None})()
        self.assertFalse(self.model_admin.has_add_permission(request))
        self.assertFalse(self.model_admin.has_change_permission(request, obj=None))
        self.assertFalse(self.model_admin.has_delete_permission(request, obj=None))

    def test_job_or_session_with_session(self):
        session = ChatSession.objects.create()
        record = LLMCostTracking.objects.create(
            session=session,
            model_name="gemini-3.6-flash",
            session_total_tokens=100,
            session_cost=0.001,
            total_cost=0.001,
        )
        result = self.model_admin.job_or_session(record)
        self.assertIn("Session", result)
        self.assertIn(str(session.id)[:8], result)

    def test_job_or_session_with_job(self):
        record = LLMCostTracking.objects.create(
            job_name="test_job",
            model_name="gemini-3.6-flash",
            session_total_tokens=100,
            session_cost=0.001,
            total_cost=0.001,
        )
        result = self.model_admin.job_or_session(record)
        self.assertEqual(result, "Job: test_job")

    def test_job_or_session_with_both(self):
        session = ChatSession.objects.create()
        record = LLMCostTracking.objects.create(
            session=session,
            job_name="both_job",
            model_name="gemini-3.6-flash",
            session_total_tokens=100,
            session_cost=0.001,
            total_cost=0.001,
        )
        result = self.model_admin.job_or_session(record)
        self.assertIn("Session", result)

    def test_job_or_session_neither(self):
        record = LLMCostTracking.objects.create(
            model_name="gemini-3.6-flash",
            session_total_tokens=100,
            session_cost=0.001,
            total_cost=0.001,
        )
        result = self.model_admin.job_or_session(record)
        self.assertEqual(result, "-")
