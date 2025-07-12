from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """
        This method is called when the Django application is ready.
        We import our signals here to ensure they are connected.
        """
        import api.signals  # noqa: F401
