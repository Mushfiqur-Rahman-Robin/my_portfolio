from django.test import TestCase
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from ..throttles import ChatbotRateThrottle, ContactFormRateThrottle, CustomAnonRateThrottle, CustomUserRateThrottle, VisitorCountRateThrottle


class ThrottleTests(TestCase):
    def test_custom_anon_throttle_scope(self):
        throttle = CustomAnonRateThrottle()
        self.assertEqual(throttle.scope, "anon")

    def test_custom_user_throttle_scope(self):
        throttle = CustomUserRateThrottle()
        self.assertEqual(throttle.scope, "user")

    def test_contact_form_throttle_scope(self):
        throttle = ContactFormRateThrottle()
        self.assertEqual(throttle.scope, "contact_form")

    def test_visitor_count_throttle_scope(self):
        throttle = VisitorCountRateThrottle()
        self.assertEqual(throttle.scope, "visitor_count")

    def test_chatbot_throttle_scope(self):
        throttle = ChatbotRateThrottle()
        self.assertEqual(throttle.scope, "chatbot")

    def test_all_throttles_inherit_correctly(self):
        self.assertTrue(issubclass(CustomAnonRateThrottle, AnonRateThrottle))
        self.assertTrue(issubclass(CustomUserRateThrottle, UserRateThrottle))
        self.assertTrue(issubclass(ContactFormRateThrottle, AnonRateThrottle))
        self.assertTrue(issubclass(VisitorCountRateThrottle, AnonRateThrottle))
        self.assertTrue(issubclass(ChatbotRateThrottle, AnonRateThrottle))
