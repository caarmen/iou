from django.urls import path

from . import views

app_name = "passkeys"
urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "register-finish/",
        views.register_finish,
        name="register-finish",
    ),
    path(
        "login-start/",
        views.login_start,
        name="login-start",
    ),
    path(
        "login-finish/",
        views.login_finish,
        name="login-finish",
    ),
]
