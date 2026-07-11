from django.test import TestCase

from ..apps import ApiConfig


class ApiConfigTests(TestCase):
    def test_app_name(self):
        self.assertEqual(ApiConfig.name, "api")

    def test_default_auto_field(self):
        self.assertEqual(ApiConfig.default_auto_field, "django.db.models.BigAutoField")

    def test_ready_imports_signals(self):
        config = ApiConfig.create("api")
        self.assertIsNotNone(config)
