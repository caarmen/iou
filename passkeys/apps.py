from django.apps import AppConfig
from django.urls import reverse_lazy


class PasskeysConfig(AppConfig):
    name = "passkeys"

    def ready(self):
        from django.conf import settings

        settings.LOGIN_URL = reverse_lazy("passkeys:login-start")
