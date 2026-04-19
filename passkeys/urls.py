from django.urls import path

from . import views

app_name = "passkeys"
urlpatterns = [
    path(
        "register-start/",
        views.register_start,
        name="register-start",
    ),
    path(
        "register-finish/",
        views.register_finish,
        name="register-finish",
    ),
]
