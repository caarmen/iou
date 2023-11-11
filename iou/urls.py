from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # ex: /iou/
    path("", views.index, name="index"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(next_page="iou"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    path("delete/<int:debt_id>/", views.delete, name="delete"),
    path("site.webmanifest", views.webmanifest, name="webmanifest"),
]
