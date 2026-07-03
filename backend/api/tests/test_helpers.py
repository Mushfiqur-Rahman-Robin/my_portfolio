from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from ..models import ChatSession, Project, Tag
from ..views import ChatbotView, get_client_ip, get_country_for_ip, get_device_type


def _make_image_file():
    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, "png")
    buf.name = "test_filter.png"
    buf.seek(0)
    return SimpleUploadedFile(buf.name, buf.read(), content_type="image/png")


class GetClientIPTests(TestCase):
    def test_x_forwarded_for_single(self):
        request = APIRequestFactory().post("/", {}, HTTP_X_FORWARDED_FOR="1.2.3.4")
        self.assertEqual(get_client_ip(request), "1.2.3.4")

    def test_x_forwarded_for_multiple(self):
        request = APIRequestFactory().post("/", {}, HTTP_X_FORWARDED_FOR="1.2.3.4, 5.6.7.8")
        self.assertEqual(get_client_ip(request), "1.2.3.4")

    def test_x_real_ip(self):
        request = APIRequestFactory().post("/", {}, HTTP_X_REAL_IP="10.0.0.1")
        self.assertEqual(get_client_ip(request), "10.0.0.1")

    def test_x_forwarded_for_takes_priority_over_x_real_ip(self):
        request = APIRequestFactory().post(
            "/",
            {},
            HTTP_X_FORWARDED_FOR="1.2.3.4",
            HTTP_X_REAL_IP="10.0.0.1",
        )
        self.assertEqual(get_client_ip(request), "1.2.3.4")

    def test_remote_addr(self):
        request = APIRequestFactory().post("/", {}, REMOTE_ADDR="192.168.1.1")
        self.assertEqual(get_client_ip(request), "192.168.1.1")

    def test_no_ip_available(self):
        request = APIRequestFactory().post("/", {})
        request.META.pop("REMOTE_ADDR", None)
        self.assertIsNone(get_client_ip(request))


class GetCountryForIPTests(TestCase):
    def test_private_ip_returns_private_local(self):
        self.assertEqual(get_country_for_ip("192.168.1.1"), "Private/Local")

    def test_localhost_returns_private_local(self):
        self.assertEqual(get_country_for_ip("127.0.0.1"), "Private/Local")

    def test_loopback_ipv6_returns_private_local(self):
        self.assertEqual(get_country_for_ip("::1"), "Private/Local")

    def test_none_ip_returns_unknown(self):
        self.assertEqual(get_country_for_ip(None), "Unknown")

    def test_empty_ip_returns_unknown(self):
        self.assertEqual(get_country_for_ip(""), "Unknown")

    def test_invalid_ip_returns_unknown(self):
        self.assertEqual(get_country_for_ip("not-an-ip"), "Unknown")

    @patch("api.views.http_client.HTTPSConnection")
    def test_external_ip_api_success(self, mock_conn_cls):
        mock_conn = mock_conn_cls.return_value
        mock_resp = mock_conn.getresponse.return_value
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"country_name": "Bangladesh"}'

        result = get_country_for_ip("103.21.244.1")
        self.assertEqual(result, "Bangladesh")

    @patch("api.views.http_client.HTTPSConnection")
    def test_external_ip_api_uses_country_fallback(self, mock_conn_cls):
        mock_conn = mock_conn_cls.return_value
        mock_resp = mock_conn.getresponse.return_value
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"country": "France"}'

        result = get_country_for_ip("8.8.8.8")
        self.assertEqual(result, "France")

    @patch("api.views.http_client.HTTPSConnection")
    def test_external_ip_api_unknown_on_error_status(self, mock_conn_cls):
        mock_conn = mock_conn_cls.return_value
        mock_resp = mock_conn.getresponse.return_value
        mock_resp.status = 500

        result = get_country_for_ip("8.8.8.8")
        self.assertEqual(result, "Unknown")

    @patch("api.views.http_client.HTTPSConnection")
    def test_external_ip_api_unknown_on_timeout(self, mock_conn_cls):
        mock_conn_cls.side_effect = TimeoutError("Timeout")

        result = get_country_for_ip("8.8.8.8")
        self.assertEqual(result, "Unknown")

    @patch("api.views.http_client.HTTPSConnection")
    def test_external_ip_api_unknown_on_json_error(self, mock_conn_cls):
        mock_conn = mock_conn_cls.return_value
        mock_resp = mock_conn.getresponse.return_value
        mock_resp.status = 200
        mock_resp.read.return_value = b"not json"

        result = get_country_for_ip("8.8.8.8")
        self.assertEqual(result, "Unknown")


class GetDeviceTypeTests(TestCase):
    def test_desktop_chrome(self):
        request = APIRequestFactory().post("/", {}, HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")
        self.assertEqual(get_device_type(request), "desktop")

    def test_mobile_iphone(self):
        request = APIRequestFactory().post("/", {}, HTTP_USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile Safari")
        self.assertEqual(get_device_type(request), "mobile")

    def test_mobile_android(self):
        request = APIRequestFactory().post("/", {}, HTTP_USER_AGENT="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit")
        self.assertEqual(get_device_type(request), "mobile")

    def test_tablet_ipad(self):
        request = APIRequestFactory().post("/", {}, HTTP_USER_AGENT="Mozilla/5.0 (iPad; CPU OS 17_0)")
        self.assertEqual(get_device_type(request), "tablet")

    def test_tablet_android(self):
        request = APIRequestFactory().post("/", {}, HTTP_USER_AGENT="Mozilla/5.0 (Linux; Android 14; Tablet K100)")
        self.assertEqual(get_device_type(request), "tablet")

    def test_unknown_no_user_agent(self):
        request = APIRequestFactory().post("/", {})
        request.META.pop("HTTP_USER_AGENT", None)
        self.assertEqual(get_device_type(request), "unknown")

    def test_unknown_empty_user_agent(self):
        request = APIRequestFactory().post("/", {}, HTTP_USER_AGENT="")
        self.assertEqual(get_device_type(request), "unknown")


class BuildConversationContextTests(TestCase):
    def test_empty_session(self):
        session = ChatSession.objects.create()
        context = ChatbotView.build_conversation_context(session)
        self.assertEqual(context, "")

    def test_single_interaction(self):
        session = ChatSession.objects.create()
        session.messages.create(sender="user", message="Hello")
        session.messages.create(sender="bot", message="Hi there!")
        context = ChatbotView.build_conversation_context(session)
        self.assertIn("User: Hello", context)
        self.assertIn("Assistant: Hi there!", context)

    def test_limits_to_last_20_interactions(self):
        session = ChatSession.objects.create()
        for idx in range(1, 26):
            session.messages.create(sender="user", message=f"question-{idx}")
            session.messages.create(sender="bot", message=f"answer-{idx}")

        context = ChatbotView.build_conversation_context(session)
        self.assertNotIn("question-5", context)
        self.assertIn("question-6", context)
        self.assertIn("question-25", context)

    def test_less_than_limit(self):
        session = ChatSession.objects.create()
        for idx in range(1, 6):
            session.messages.create(sender="user", message=f"q{idx}")
            session.messages.create(sender="bot", message=f"a{idx}")

        context = ChatbotView.build_conversation_context(session)
        self.assertIn("q1", context)
        self.assertIn("q5", context)


class ChatbotViewEdgeCaseTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_missing_query_returns_400(self):
        response = self.client.post(reverse("chatbot"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @override_settings(GEMINI_API_KEY="test-key", LLM_PROVIDER="gemini")  # pragma: allowlist secret
    @patch("api.views.query_nodes")
    @patch("api.views.generate_chat_completion")
    def test_invalid_session_id_creates_new(self, mock_generate, mock_query_nodes):
        mock_query_nodes.return_value = {"documents": [["context"]]}
        mock_generate.return_value = "answer"

        response = self.client.post(
            reverse("chatbot"),
            {"query": "hello", "session_id": "00000000-0000-0000-0000-000000000000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["session_id"], "00000000-0000-0000-0000-000000000000")

    def test_no_experiences_or_publications_still_works(self):

        with override_settings(GEMINI_API_KEY="test-key", LLM_PROVIDER="gemini"):  # pragma: allowlist secret
            with patch("api.views.query_nodes") as mock_query:
                with patch("api.views.generate_chat_completion") as mock_generate:
                    mock_query.return_value = {"documents": [[""]]}
                    mock_generate.return_value = "no info"

                    response = self.client.post(
                        reverse("chatbot"),
                        {"query": "tell me about experience"},
                        format="json",
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(GEMINI_API_KEY="test-key", LLM_PROVIDER="gemini")  # pragma: allowlist secret
    @patch("api.views.generate_chat_completion", side_effect=Exception("LLM API down"))
    @patch("api.views.query_nodes", return_value={"documents": [[""]]})
    def test_chatbot_returns_500_on_fatal_error(self, mock_query, mock_generate):
        response = self.client.post(reverse("chatbot"), {"query": "hello"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)


class ProjectFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        tag_py = Tag.objects.create(name="Python")
        tag_js = Tag.objects.create(name="JS")
        img = _make_image_file()
        self.proj1 = Project.objects.create(
            title="Featured Python Project",
            description="desc",
            image=img,
            is_featured=True,
            display_order=1,
        )
        self.proj1.tags.add(tag_py)
        img2 = _make_image_file()
        self.proj2 = Project.objects.create(
            title="JS Project",
            description="desc",
            image=img2,
            is_featured=False,
            display_order=2,
        )
        self.proj2.tags.add(tag_js)

    def test_filter_by_tag(self):
        response = self.client.get(reverse("project-list") + "?tag=Python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Featured Python Project")

    def test_filter_by_is_featured_true(self):
        response = self.client.get(reverse("project-list") + "?is_featured=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Featured Python Project")

    def test_filter_by_is_featured_false(self):
        response = self.client.get(reverse("project-list") + "?is_featured=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "JS Project")

    def test_filter_by_tag_case_insensitive(self):
        response = self.client.get(reverse("project-list") + "?tag=python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class ContactMessageEmailFailureTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    @patch("api.views.send_mail", side_effect=Exception("SMTP error"))
    def test_contact_message_still_created_on_email_failure(self, mock_send):
        message_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Hello",
        }
        response = self.client.post(reverse("message-list"), message_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIn("name", response.data)


class VisitorCountErrorTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.throttles.VisitorCountRateThrottle.allow_request", return_value=True)
    @patch("api.views.VisitorAnalytics.objects.create", side_effect=Exception("DB write failed"))
    def test_visitor_count_handles_analytics_error_gracefully(self, mock_create, _mock_allow):
        response = self.client.post(
            reverse("visitor-count"),
            {},
            format="json",
            HTTP_X_FORWARDED_FOR="203.0.113.1",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)

    @patch("api.throttles.VisitorCountRateThrottle.allow_request", return_value=True)
    @patch("api.views.TotalVisitorCount.objects.get_or_create", side_effect=Exception("Fatal DB error"))
    def test_visitor_count_returns_500_on_fatal_error(self, mock_get_or_create, _mock_allow):
        response = self.client.post(reverse("visitor-count"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
