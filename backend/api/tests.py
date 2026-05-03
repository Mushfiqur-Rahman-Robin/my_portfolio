# api/tests.py
import os
import shutil
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .models import Achievement, Certification, ChatSession, Experience, Project, Publication, Tag, VisitorAnalytics
from .prompt import build_chatbot_prompt
from .views import ChatbotView, get_country_for_ip, get_device_type

# Define the temporary media root path
# This should be outside the TestCase class definition but can use settings.BASE_DIR
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media")


def generate_photo_file():
    file = BytesIO()
    image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
    image.save(file, "png")
    file.name = "test_image.png"
    file.seek(0)
    return SimpleUploadedFile(file.name, file.read(), content_type="image/png")


# Apply the override for MEDIA_ROOT to the entire test class
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class APITests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure the test media directory exists before tests run
        os.makedirs(TEST_MEDIA_ROOT, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Clean up the test media directory after all tests in the class have run
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    def setUp(self):
        self.client = APIClient()
        self.admin_client = APIClient()
        self.request_factory = APIRequestFactory()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",  # pragma: allowlist secret # nosec: B106
            email="admin@example.com",  # pragma: allowlist secret # nosec: B106
            password="testpass123",  # pragma: allowlist secret # nosec: B106
        )
        self.admin_client.force_authenticate(user=self.admin_user)
        self.tag = Tag.objects.create(name="Test Tag")

        # This setup is for objects that already exist before each test runs.
        # The image is created in memory and saved to the test database.
        self.project = Project.objects.create(
            title="Test Project",
            description="A test project",
            image=generate_photo_file(),
            display_order=1,
        )
        self.project.tags.add(self.tag)

        self.publication = Publication.objects.create(
            title="Test Publication",
            authors="John Doe",
            conference="TestConf",
            publication_url="https://example.com",
            published_date="2025-01-01",
            display_order=1,
        )
        self.certification = Certification.objects.create(
            name="Test Certification",
            issuing_organization="Test Org",
            credential_url="https://example.com",
            issue_date="2025-01-01",
            display_order=1,
        )
        self.achievement = Achievement.objects.create(
            title="Test Achievement",
            description="A test achievement",
            date="2025-01-01",
            display_order=1,
        )
        self.experience = Experience.objects.create(
            company_name="Test Company",
            job_title="Test Engineer",
            start_date="2024-01-01",
            end_date="2025-01-01",
            is_current=False,
            work_details="Test details",
            display_order=1,
        )

    def test_get_projects(self):
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Project")

    def test_create_project(self):
        """
        Test creating a project with an image upload.
        This requires using format='multipart' instead of 'json'.
        """
        new_project_data = {
            "title": "New Project",
            "description": "Another test project",
            "image": generate_photo_file(),  # Generate a new file for the upload
            "display_order": 2,
            "tags": [self.tag.name],
        }
        # CRITICAL FIX: Use format='multipart' for file uploads
        response = self.admin_client.post(reverse("project-list"), new_project_data, format="multipart")

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data["title"], "New Project")
        self.assertTrue(response.data["image"].endswith(".webp"))

    def test_update_project(self):
        url = reverse("project-detail", args=[self.project.id])
        updated_data = {"title": "Updated Project"}
        # PATCHing a simple field can still use 'json' format
        response = self.admin_client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated Project")

    def test_create_project_requires_admin(self):
        new_project_data = {
            "title": "Unauthorized Project",
            "description": "Another test project",
            "image": generate_photo_file(),
            "display_order": 2,
            "tags": [self.tag.name],
        }
        response = self.client.post(reverse("project-list"), new_project_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_new_image_upload_is_stored_as_webp(self):
        self.assertTrue(self.project.image.name.endswith(".webp"))

    def test_legacy_non_webp_image_stays_unchanged_when_image_not_reuploaded(self):
        Project.objects.filter(pk=self.project.pk).update(image="projects/banners/legacy-image.png")
        self.project.refresh_from_db()

        self.project.title = "Updated Title Only"
        self.project.save(update_fields=["title"])
        self.project.refresh_from_db()

        self.assertTrue(self.project.image.name.endswith("legacy-image.png"))

    def test_delete_project(self):
        url = reverse("project-detail", args=[self.project.id])
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_get_publications(self):
        response = self.client.get(reverse("publication-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Publication")

    def test_get_certifications(self):
        response = self.client.get(reverse("certification-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Certification")

    def test_get_achievements(self):
        response = self.client.get(reverse("achievement-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Achievement")

    def test_create_tag_not_allowed(self):
        """
        Tags are read-only from the API, so POST should be disallowed.
        """
        url = reverse("tag-list")
        tag_data = {"name": "New Tag"}
        response = self.client.post(url, tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_experiences(self):
        response = self.client.get(reverse("experience-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["company_name"], "Test Company")

    @patch("api.views.get_country_for_ip")
    @patch("api.throttles.VisitorCountRateThrottle.allow_request", return_value=True)
    def test_visitor_count_tracks_ip_country_and_device_type(self, _mock_allow_request, mock_country_lookup):
        mock_country_lookup.return_value = "Bangladesh"

        response = self.client.post(
            reverse("visitor-count"),
            {},
            format="json",
            HTTP_X_FORWARDED_FOR="103.21.244.1, 127.0.0.1",
            HTTP_USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VisitorAnalytics.objects.count(), 1)

        analytics = VisitorAnalytics.objects.first()
        self.assertEqual(str(analytics.ip_address), "103.21.244.1")
        self.assertEqual(analytics.country, "Bangladesh")
        self.assertEqual(analytics.device_type, "mobile")

    @patch("api.views.get_country_for_ip")
    @patch("api.throttles.VisitorCountRateThrottle.allow_request", return_value=True)
    def test_visitor_count_tracks_multiple_entries_for_repeated_same_day_visits(
        self,
        _mock_allow_request,
        mock_country_lookup,
    ):
        mock_country_lookup.return_value = "Bangladesh"

        headers = {
            "HTTP_X_FORWARDED_FOR": "103.21.244.1, 127.0.0.1",
            "HTTP_USER_AGENT": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
        }

        first = self.client.post(reverse("visitor-count"), {}, format="json", **headers)
        second = self.client.post(reverse("visitor-count"), {}, format="json", **headers)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(VisitorAnalytics.objects.count(), 2)

    def test_chatbot_conversation_context_uses_last_20_interactions(self):
        session = ChatSession.objects.create()

        for index in range(1, 26):
            session.messages.create(sender="user", message=f"question-{index}")
            session.messages.create(sender="bot", message=f"answer-{index}")

        context = ChatbotView.build_conversation_context(session)

        self.assertNotIn("User: question-5\n", context)
        self.assertNotIn("Assistant: answer-5\n", context)
        self.assertIn("User: question-6\n", context)
        self.assertIn("Assistant: answer-6\n", context)
        self.assertIn("User: question-25", context)
        self.assertIn("Assistant: answer-25", context)

    def test_prompt_builder_keeps_placeholder_like_text_intact(self):
        query = "Can you explain value {x} and config ${NAME}?"
        history = "User: hello {user}"
        context = "Project token: {{abc}}"

        prompt = build_chatbot_prompt(query=query, conversation_context=history, final_context=context)

        self.assertIn(query, prompt)
        self.assertIn(history, prompt)
        self.assertIn(context, prompt)

    def test_prompt_builder_uses_safe_defaults_for_missing_inputs(self):
        prompt = build_chatbot_prompt(query=None, conversation_context=None, final_context=None)

        self.assertIn("No prior messages in this session.", prompt)
        self.assertIn("No relevant information found in the knowledge base.", prompt)

    def test_country_lookup_returns_private_local_for_private_ip(self):
        country = get_country_for_ip("127.0.0.1")
        self.assertEqual(country, "Private/Local")

    def test_device_type_detects_unknown_when_no_user_agent(self):
        request = self.request_factory.post(reverse("visitor-count"), {}, format="json")
        request.META.pop("HTTP_USER_AGENT", None)

        self.assertEqual(get_device_type(request), "unknown")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_contact_message_sends_email(self):
        """
        Test that sending a contact message also sends an email.
        """
        self.assertEqual(len(mail.outbox), 0)  # No email sent initially

        message_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message.",
        }
        response = self.client.post(reverse("message-list"), message_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)  # One email should have been sent

        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "New Contact Message from Portfolio Website")
        self.assertIn("Name: Test User", sent_email.body)
        self.assertIn("Email: test@example.com", sent_email.body)
        self.assertIn("Message:\nThis is a test message.", sent_email.body)
        self.assertEqual(sent_email.from_email, settings.DEFAULT_FROM_EMAIL)

        self.assertIn(settings.ADMIN_EMAIL, sent_email.to)

    @override_settings(OPENAI_API_KEY="test-key")  # pragma: allowlist secret
    @patch("api.views.query_nodes")
    @patch("api.views.OpenAI")
    def test_chatbot_uses_session_history_for_follow_up(self, mock_openai, mock_query_nodes):
        mock_query_nodes.return_value = {"documents": [["portfolio context"]]}

        completion_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Test bot answer"))])
        mock_openai.return_value.chat.completions.create.return_value = completion_response

        first = self.client.post(reverse("chatbot"), {"query": "what is mushfiq's motto?"}, format="json")
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        session_id = first.data["session_id"]

        second = self.client.post(
            reverse("chatbot"),
            {"query": "what was my first question?", "session_id": session_id},
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_200_OK)

        create_calls = mock_openai.return_value.chat.completions.create.call_args_list
        self.assertEqual(len(create_calls), 2)
        second_prompt = create_calls[1].kwargs["messages"][0]["content"]

        self.assertIn("---RECENT CONVERSATION HISTORY---", second_prompt)
        self.assertIn("User: what is mushfiq's motto?", second_prompt)
        self.assertIn("User: what was my first question?", second_prompt)

        session = ChatSession.objects.get(id=session_id)
        self.assertEqual(session.messages.count(), 4)
