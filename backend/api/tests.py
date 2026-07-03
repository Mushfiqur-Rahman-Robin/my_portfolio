# api/tests.py
import os
import shutil
from io import BytesIO
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

from .llm_client import generate_chat_completion, generate_embedding
from .models import Achievement, Certification, ChatSession, Experience, LLMCostTracking, Project, Publication, Tag, VisitorAnalytics
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

    @override_settings(GEMINI_API_KEY="test-key", LLM_PROVIDER="gemini")  # pragma: allowlist secret
    @patch("api.views.query_nodes")
    @patch("api.views.generate_chat_completion")
    def test_chatbot_uses_session_history_for_follow_up(self, mock_generate, mock_query_nodes):
        mock_query_nodes.return_value = {"documents": [["portfolio context"]]}

        mock_generate.return_value = "Test bot answer"

        first = self.client.post(reverse("chatbot"), {"query": "what is mushfiq's motto?"}, format="json")
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        session_id = first.data["session_id"]

        second = self.client.post(
            reverse("chatbot"),
            {"query": "what was my first question?", "session_id": session_id},
            format="json",
        )
        self.assertEqual(second.status_code, status.HTTP_200_OK)

        create_calls = mock_generate.call_args_list
        self.assertEqual(len(create_calls), 2)
        second_prompt = create_calls[1].kwargs["messages"][0]["content"]

        self.assertIn("---RECENT CONVERSATION HISTORY---", second_prompt)
        self.assertIn("User: what is mushfiq's motto?", second_prompt)
        self.assertIn("User: what was my first question?", second_prompt)

        session = ChatSession.objects.get(id=session_id)
        self.assertEqual(session.messages.count(), 4)


class LLMClientTests(TestCase):
    """
    Unit tests for api/llm_client.py.

    All external API calls (Gemini and OpenAI) are mocked so no real network
    traffic is produced during the test run.
    """

    # ------------------------------------------------------------------
    # Model selection helpers
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="")
    def test_get_chat_model_gemini_default(self):
        from .llm_client import get_chat_model

        self.assertEqual(get_chat_model(), "gemini-2.5-flash")

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="")
    def test_get_chat_model_openai_default(self):
        from .llm_client import get_chat_model

        self.assertEqual(get_chat_model(), "gpt-4.1-mini")

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="gemini-2.0-flash")
    def test_get_chat_model_custom_override(self):
        from .llm_client import get_chat_model

        self.assertEqual(get_chat_model(), "gemini-2.0-flash")

    @override_settings(LLM_PROVIDER="gemini")
    def test_get_embedding_model_gemini(self):
        from .llm_client import get_embedding_model

        self.assertEqual(get_embedding_model(), "gemini-embedding-2")

    @override_settings(LLM_PROVIDER="openai")
    def test_get_embedding_model_openai(self):
        from .llm_client import get_embedding_model

        self.assertEqual(get_embedding_model(), "text-embedding-3-small")

    @override_settings(LLM_PROVIDER="gemini")
    def test_get_embedding_dimension_gemini(self):
        from .llm_client import get_embedding_dimension

        self.assertEqual(get_embedding_dimension(), 1536)

    @override_settings(LLM_PROVIDER="openai")
    def test_get_embedding_dimension_openai(self):
        from .llm_client import get_embedding_dimension

        self.assertEqual(get_embedding_dimension(), 1536)

    # ------------------------------------------------------------------
    # Chat completion — Gemini path
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="fake-gemini-key")  # pragma: allowlist secret
    @patch("api.llm_client.genai")
    def test_generate_chat_completion_gemini(self, mock_genai):
        """Gemini provider routes correctly and returns the model's text."""
        from .llm_client import generate_chat_completion

        mock_response = mock_genai.Client.return_value.models.generate_content.return_value
        mock_response.text = "Hello from Gemini!"

        result = generate_chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=100,
            temperature=0.5,
        )

        self.assertEqual(result, "Hello from Gemini!")
        mock_genai.Client.assert_called_once_with(api_key="fake-gemini-key")  # pragma: allowlist secret
        mock_genai.Client.return_value.models.generate_content.assert_called_once()

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="")
    def test_generate_chat_completion_gemini_missing_key_raises(self):
        """Missing GEMINI_API_KEY with gemini provider raises ValueError."""
        from .llm_client import generate_chat_completion

        with self.assertRaises(ValueError, msg="GEMINI_API_KEY is not set"):
            generate_chat_completion(messages=[{"role": "user", "content": "Hi"}])

    # ------------------------------------------------------------------
    # Chat completion — OpenAI path
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="", OPENAI_API_KEY="fake-openai-key")  # pragma: allowlist secret
    @patch("api.llm_client.OpenAI")
    def test_generate_chat_completion_openai(self, mock_openai_cls):
        """OpenAI provider routes correctly and returns the model's text."""
        from .llm_client import generate_chat_completion

        mock_choice = mock_openai_cls.return_value.chat.completions.create.return_value.choices[0]
        mock_choice.message.content = "Hello from OpenAI!"

        result = generate_chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=100,
            temperature=0.5,
        )

        self.assertEqual(result, "Hello from OpenAI!")
        mock_openai_cls.assert_called_once_with(api_key="fake-openai-key")  # pragma: allowlist secret

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="", OPENAI_API_KEY="")
    def test_generate_chat_completion_openai_missing_key_raises(self):
        """Missing OPENAI_API_KEY with openai provider raises ValueError."""
        from .llm_client import generate_chat_completion

        with self.assertRaises(ValueError, msg="OPENAI_API_KEY is not set"):
            generate_chat_completion(messages=[{"role": "user", "content": "Hi"}])

    # ------------------------------------------------------------------
    # Embedding — Gemini path
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="fake-gemini-key")  # pragma: allowlist secret
    @patch("api.llm_client.genai")
    def test_generate_embedding_gemini(self, mock_genai):
        """Gemini embedding path returns a list of floats."""
        from .llm_client import generate_embedding

        mock_embedding = mock_genai.Client.return_value.models.embed_content.return_value
        mock_embedding.embeddings = [type("Emb", (), {"values": [0.1, 0.2, 0.3]})()]

        result = generate_embedding("test text")

        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_genai.Client.return_value.models.embed_content.assert_called_once()

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="")
    def test_generate_embedding_gemini_missing_key_raises(self):
        """Missing GEMINI_API_KEY with gemini provider raises ValueError for embedding."""
        from .llm_client import generate_embedding

        with self.assertRaises(ValueError, msg="GEMINI_API_KEY is not set"):
            generate_embedding("test text")

    # ------------------------------------------------------------------
    # Embedding — OpenAI path
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="", OPENAI_API_KEY="fake-openai-key")  # pragma: allowlist secret
    @patch("api.llm_client.OpenAI")
    def test_generate_embedding_openai(self, mock_openai_cls):
        """OpenAI embedding path returns a list of floats."""
        from .llm_client import generate_embedding

        mock_data = mock_openai_cls.return_value.embeddings.create.return_value.data[0]
        mock_data.embedding = [0.4, 0.5, 0.6]

        result = generate_embedding("test text")

        self.assertEqual(result, [0.4, 0.5, 0.6])
        mock_openai_cls.return_value.embeddings.create.assert_called_once()

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="", OPENAI_API_KEY="")
    def test_generate_embedding_openai_missing_key_raises(self):
        """Missing OPENAI_API_KEY with openai provider raises ValueError for embedding."""
        from .llm_client import generate_embedding

        with self.assertRaises(ValueError, msg="OPENAI_API_KEY is not set"):
            generate_embedding("test text")


class LLMCostTrackingTests(TestCase):
    """Tests for LLM cost tracking ledger entries and running totals."""

    # ------------------------------------------------------------------
    # Basic record creation
    # ------------------------------------------------------------------

    def test_chat_cost_tracking_creates_record_with_session(self):
        session = ChatSession.objects.create()

        from .llm_client import record_llm_cost

        record_llm_cost("chat", "gemini-2.5-flash", 1000, 200, session=session)

        record = LLMCostTracking.objects.first()
        self.assertIsNotNone(record)
        self.assertEqual(record.operation_type, "chat")
        self.assertEqual(record.model_name, "gemini-2.5-flash")
        self.assertEqual(record.tokens_used, 1200)
        self.assertEqual(record.session, session)

    def test_chat_cost_tracking_without_session(self):
        from .llm_client import record_llm_cost

        record_llm_cost("chat", "gpt-4.1-mini", 500, 150, session=None)

        record = LLMCostTracking.objects.first()
        self.assertIsNotNone(record)
        self.assertIsNone(record.session)

    def test_embedding_cost_tracking_creates_record(self):
        from .llm_client import record_llm_cost

        record_llm_cost("embedding", "text-embedding-3-small", 300, 0)

        record = LLMCostTracking.objects.first()
        self.assertIsNotNone(record)
        self.assertEqual(record.operation_type, "embedding")
        self.assertEqual(record.model_name, "text-embedding-3-small")
        self.assertEqual(record.tokens_used, 300)
        self.assertIsNone(record.session)

    # ------------------------------------------------------------------
    # Running totals — sequential chat accumulation
    # ------------------------------------------------------------------

    def test_running_totals_accumulate_for_chat(self):
        from .llm_client import record_llm_cost

        session = ChatSession.objects.create()

        record_llm_cost("chat", "gemini-2.5-flash", 1000, 200, session=session)
        record_llm_cost("chat", "gemini-2.5-flash", 500, 100, session=session)
        record_llm_cost("chat", "gemini-2.5-flash", 300, 50, session=session)

        records = list(LLMCostTracking.objects.order_by("created_at"))
        self.assertEqual(len(records), 3)

        self.assertEqual(records[0].total_chat_tokens, 1200)
        self.assertEqual(records[0].total_embedding_tokens, 0)
        self.assertEqual(records[0].total_tokens, 1200)

        self.assertEqual(records[1].total_chat_tokens, 1800)
        self.assertEqual(records[1].total_embedding_tokens, 0)
        self.assertEqual(records[1].total_tokens, 1800)

        self.assertEqual(records[2].total_chat_tokens, 2150)
        self.assertEqual(records[2].total_embedding_tokens, 0)
        self.assertEqual(records[2].total_tokens, 2150)

    # ------------------------------------------------------------------
    # Running totals — sequential embedding accumulation
    # ------------------------------------------------------------------

    def test_running_totals_accumulate_for_embedding(self):
        from .llm_client import record_llm_cost

        record_llm_cost("embedding", "gemini-embedding-2", 500, 0)
        record_llm_cost("embedding", "gemini-embedding-2", 300, 0)
        record_llm_cost("embedding", "gemini-embedding-2", 200, 0)

        records = list(LLMCostTracking.objects.order_by("created_at"))
        self.assertEqual(len(records), 3)

        self.assertEqual(records[0].total_chat_tokens, 0)
        self.assertEqual(records[0].total_embedding_tokens, 500)

        self.assertEqual(records[1].total_chat_tokens, 0)
        self.assertEqual(records[1].total_embedding_tokens, 800)

        self.assertEqual(records[2].total_chat_tokens, 0)
        self.assertEqual(records[2].total_embedding_tokens, 1000)

    # ------------------------------------------------------------------
    # Running totals — mixed chat + embedding accumulation
    # ------------------------------------------------------------------

    def test_mixed_chat_and_embedding_running_totals(self):
        from .llm_client import record_llm_cost

        session = ChatSession.objects.create()

        record_llm_cost("chat", "gemini-2.5-flash", 1000, 200, session=session)
        record_llm_cost("embedding", "gemini-embedding-2", 400, 0)
        record_llm_cost("chat", "gemini-2.5-flash", 300, 100, session=session)
        record_llm_cost("embedding", "gemini-embedding-2", 200, 0)

        records = list(LLMCostTracking.objects.order_by("created_at"))
        self.assertEqual(len(records), 4)

        # Record 1: chat 1200 tokens
        self.assertEqual(records[0].tokens_used, 1200)
        self.assertEqual(records[0].total_chat_tokens, 1200)
        self.assertEqual(records[0].total_embedding_tokens, 0)
        self.assertEqual(records[0].total_tokens, 1200)
        self.assertGreater(float(records[0].total_chat_cost), 0)
        self.assertEqual(float(records[0].total_embedding_cost), 0)

        # Record 2: embedding 400 tokens
        self.assertEqual(records[1].tokens_used, 400)
        self.assertEqual(records[1].total_chat_tokens, 1200)
        self.assertEqual(records[1].total_embedding_tokens, 400)
        self.assertEqual(records[1].total_tokens, 1600)
        self.assertEqual(float(records[1].total_chat_cost), float(records[0].total_chat_cost))
        self.assertGreater(float(records[1].total_embedding_cost), 0)

        # Record 3: chat 400 tokens
        self.assertEqual(records[2].tokens_used, 400)
        self.assertEqual(records[2].total_chat_tokens, 1600)
        self.assertEqual(records[2].total_embedding_tokens, 400)
        self.assertEqual(records[2].total_tokens, 2000)

        # Record 4: embedding 200 tokens
        self.assertEqual(records[3].tokens_used, 200)
        self.assertEqual(records[3].total_chat_tokens, 1600)
        self.assertEqual(records[3].total_embedding_tokens, 600)
        self.assertEqual(records[3].total_tokens, 2200)

        # Total cost should equal sum of individual costs
        expected_total = sum(float(r.cost) for r in records)
        self.assertAlmostEqual(float(records[3].total_cost), expected_total)

    # ------------------------------------------------------------------
    # Cost calculations — specific model prices
    # ------------------------------------------------------------------

    def test_chat_cost_calculation_gemini_flash(self):
        from .pricing import calculate_chat_cost

        cost = calculate_chat_cost("gemini-2.5-flash", 1000000, 1000000)
        expected = 0.30 + 2.50
        self.assertAlmostEqual(float(cost), expected)

    def test_chat_cost_calculation_openai(self):
        from .pricing import calculate_chat_cost

        cost = calculate_chat_cost("gpt-4.1-mini", 1000000, 1000000)
        expected = 0.40 + 1.60
        self.assertAlmostEqual(float(cost), expected)

    def test_embedding_cost_calculation_openai(self):
        from .pricing import calculate_embedding_cost

        cost = calculate_embedding_cost("text-embedding-3-small", 1000000)
        self.assertAlmostEqual(float(cost), 0.02)

    def test_embedding_cost_calculation_gemini(self):
        from .pricing import calculate_embedding_cost

        cost = calculate_embedding_cost("gemini-embedding-2", 1000000)
        self.assertAlmostEqual(float(cost), 0.20)

    def test_chat_cost_zero_tokens(self):
        from .pricing import calculate_chat_cost

        cost = calculate_chat_cost("gemini-2.5-flash", 0, 0)
        self.assertEqual(cost, 0.0)

    def test_embedding_cost_zero_tokens(self):
        from .pricing import calculate_embedding_cost

        cost = calculate_embedding_cost("gemini-embedding-2", 0)
        self.assertEqual(cost, 0.0)

    def test_chat_cost_unknown_model_falls_back_to_defaults(self):
        from .pricing import DEFAULT_CHAT_INPUT_PRICE, DEFAULT_CHAT_OUTPUT_PRICE, calculate_chat_cost

        cost = calculate_chat_cost("nonexistent-model", 1000000, 1000000)
        expected = DEFAULT_CHAT_INPUT_PRICE + DEFAULT_CHAT_OUTPUT_PRICE
        self.assertAlmostEqual(float(cost), expected)

    def test_embedding_cost_unknown_model_falls_back_to_default(self):
        from .pricing import DEFAULT_EMBEDDING_PRICE, calculate_embedding_cost

        cost = calculate_embedding_cost("nonexistent-model", 1000000)
        self.assertAlmostEqual(float(cost), DEFAULT_EMBEDDING_PRICE)

    # ------------------------------------------------------------------
    # Token estimation
    # ------------------------------------------------------------------

    def test_estimate_token_count_positive(self):
        from .pricing import estimate_token_count

        tokens = estimate_token_count("Hello world, this is a test sentence.")
        self.assertGreater(tokens, 0)
        self.assertIsInstance(tokens, int)

    def test_estimate_token_count_empty_string(self):
        from .pricing import estimate_token_count

        tokens = estimate_token_count("")
        self.assertEqual(tokens, 0)

    def test_estimate_token_count_none(self):
        from .pricing import estimate_token_count

        tokens = estimate_token_count(None)
        self.assertEqual(tokens, 0)

    # ------------------------------------------------------------------
    # Chat completion — cost recording integration
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="fake-key")  # pragma: allowlist secret
    @patch("api.llm_client.genai")
    def test_chat_completion_records_cost_with_session(self, mock_genai):
        mock_response = mock_genai.Client.return_value.models.generate_content.return_value
        mock_response.text = "Hello!"

        session = ChatSession.objects.create()

        result = generate_chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            session=session,
        )
        self.assertEqual(result, "Hello!")
        self.assertEqual(LLMCostTracking.objects.count(), 1)

        record = LLMCostTracking.objects.first()
        self.assertEqual(record.operation_type, "chat")
        self.assertEqual(record.session, session)

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="fake-key")  # pragma: allowlist secret
    @patch("api.llm_client.genai")
    def test_chat_completion_no_cost_without_session(self, mock_genai):
        mock_response = mock_genai.Client.return_value.models.generate_content.return_value
        mock_response.text = "Hello!"
        mock_response.usage_metadata = None

        generate_chat_completion(messages=[{"role": "user", "content": "Hi"}])

        self.assertEqual(LLMCostTracking.objects.count(), 0)

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="fake-key")  # pragma: allowlist secret
    @patch("api.llm_client.genai")
    def test_chat_completion_extracts_usage_metadata(self, mock_genai):
        mock_response = mock_genai.Client.return_value.models.generate_content.return_value
        mock_response.text = "Hello!"
        usage = type("Usage", (), {"prompt_token_count": 42, "candidates_token_count": 7})()
        mock_response.usage_metadata = usage

        session = ChatSession.objects.create()

        generate_chat_completion(messages=[{"role": "user", "content": "Hi"}], session=session)

        record = LLMCostTracking.objects.first()
        self.assertEqual(record.tokens_used, 49)

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="", OPENAI_API_KEY="fake-key")  # pragma: allowlist secret
    @patch("api.llm_client.OpenAI")
    def test_chat_completion_extracts_openai_usage(self, mock_openai_cls):
        mock_completion = mock_openai_cls.return_value.chat.completions.create.return_value
        usage = type("Usage", (), {"prompt_tokens": 15, "completion_tokens": 8})()
        mock_completion.usage = usage
        mock_completion.choices[0].message.content = "Hello from OpenAI!"

        session = ChatSession.objects.create()

        generate_chat_completion(messages=[{"role": "user", "content": "Hi"}], session=session)

        record = LLMCostTracking.objects.first()
        self.assertEqual(record.tokens_used, 23)
        self.assertEqual(record.operation_type, "chat")

    # ------------------------------------------------------------------
    # Embedding — cost recording integration
    # ------------------------------------------------------------------

    @override_settings(LLM_PROVIDER="gemini", LLM_CHAT_MODEL="", GEMINI_API_KEY="fake-key")  # pragma: allowlist secret
    @patch("api.llm_client.genai")
    def test_embedding_records_cost(self, mock_genai):
        mock_embedding = mock_genai.Client.return_value.models.embed_content.return_value
        mock_embedding.embeddings = [type("Emb", (), {"values": [0.1, 0.2]})()]

        result = generate_embedding("hello world this is test text for embedding")

        self.assertEqual(result, [0.1, 0.2])
        self.assertEqual(LLMCostTracking.objects.count(), 1)

        record = LLMCostTracking.objects.first()
        self.assertEqual(record.operation_type, "embedding")
        self.assertGreater(record.tokens_used, 0)
        self.assertIsNone(record.session)

    @override_settings(LLM_PROVIDER="openai", LLM_CHAT_MODEL="", OPENAI_API_KEY="fake-key")  # pragma: allowlist secret
    @patch("api.llm_client.OpenAI")
    def test_embedding_records_cost_openai(self, mock_openai_cls):
        mock_resp = mock_openai_cls.return_value.embeddings.create.return_value
        mock_resp.data[0].embedding = [0.5, 0.6]
        usage = type("Usage", (), {"prompt_tokens": 10})()
        mock_resp.usage = usage

        result = generate_embedding("test")

        self.assertEqual(result, [0.5, 0.6])
        record = LLMCostTracking.objects.first()
        self.assertEqual(record.operation_type, "embedding")
        self.assertEqual(record.tokens_used, 10)

    # ------------------------------------------------------------------
    # Model __str__ and admin query count
    # ------------------------------------------------------------------

    def test_llm_cost_tracking_str(self):
        record = LLMCostTracking.objects.create(
            operation_type="chat",
            model_name="gemini-2.5-flash",
            tokens_used=100,
            cost=0.00042,
            total_cost=0.00042,
        )
        self.assertIn("Chat", str(record))
        self.assertIn("0.00042", str(record))

    def test_cost_tracking_uses_minimal_queries_per_insert(self):
        from .llm_client import record_llm_cost

        with self.assertNumQueries(4):
            record_llm_cost("chat", "gemini-2.5-flash", 100, 50)

    def test_cost_tracking_uses_minimal_queries_for_embedding(self):
        from .llm_client import record_llm_cost

        with self.assertNumQueries(4):
            record_llm_cost("embedding", "text-embedding-3-small", 200, 0)

    # ------------------------------------------------------------------
    # Concurrent safety — select_for_update used
    # ------------------------------------------------------------------

    def test_concurrent_write_safety_via_select_for_update(self):
        from .llm_client import record_llm_cost

        record_llm_cost("chat", "gemini-2.5-flash", 100, 50)
        record_llm_cost("chat", "gemini-2.5-flash", 200, 100)

        second = LLMCostTracking.objects.order_by("-created_at").first()
        self.assertEqual(second.total_tokens, 450)
