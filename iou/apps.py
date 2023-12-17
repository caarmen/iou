from django.apps import AppConfig
from django.urls import reverse_lazy


class IouConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iou"

    def ready(self):
        from django.conf import settings

        settings.LOGIN_URL = reverse_lazy("login")
