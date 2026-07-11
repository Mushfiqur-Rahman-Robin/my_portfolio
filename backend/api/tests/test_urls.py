from django.test import TestCase
from django.urls import resolve, reverse


class CoreURLTests(TestCase):
    def test_health_check_url_resolves(self):
        url = "/health/"
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "healthcheck_view")

    def test_health_check_returns_ok(self):
        response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")

    def test_admin_url_resolves(self):
        url = "/admin/"
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "index")

    def test_api_schema_url_resolves(self):
        url = "/api/schema/"
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, "schema")


class APIURLTests(TestCase):
    def test_projects_list_url_reverse(self):
        url = reverse("project-list")
        self.assertEqual(url, "/api/v1/projects/")

    def test_projects_detail_url(self):
        url = reverse("project-detail", args=["00000000-0000-0000-0000-000000000001"])
        self.assertIn("/api/v1/projects/", url)

    def test_publications_list_url(self):
        url = reverse("publication-list")
        self.assertEqual(url, "/api/v1/publications/")

    def test_certifications_list_url(self):
        url = reverse("certification-list")
        self.assertEqual(url, "/api/v1/certifications/")

    def test_achievements_list_url(self):
        url = reverse("achievement-list")
        self.assertEqual(url, "/api/v1/achievements/")

    def test_messages_list_url(self):
        url = reverse("message-list")
        self.assertEqual(url, "/api/v1/messages/")

    def test_resumes_list_url(self):
        url = reverse("resume-list")
        self.assertEqual(url, "/api/v1/resumes/")

    def test_tags_list_url(self):
        url = reverse("tag-list")
        self.assertEqual(url, "/api/v1/tags/")

    def test_experiences_list_url(self):
        url = reverse("experience-list")
        self.assertEqual(url, "/api/v1/experiences/")

    def test_experience_photos_list_url(self):
        url = reverse("experience-photo-list")
        self.assertEqual(url, "/api/v1/experience-photos/")

    def test_visitor_count_url(self):
        url = reverse("visitor-count")
        self.assertEqual(url, "/api/v1/visitor-count/")

    def test_chatbot_url(self):
        url = reverse("chatbot")
        self.assertEqual(url, "/api/v1/chatbot/")


class SchemaURLTests(TestCase):
    def test_swagger_ui_url_resolves(self):
        url = "/api/docs/"
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, "swagger-ui")

    def test_redoc_url_resolves(self):
        url = "/api/redoc/"
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, "redoc")
