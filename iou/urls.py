from django.urls import path

from . import views

urlpatterns = [
    # ex: /iou/
    path("", views.index, name="index"),
    path("site.webmanifest", views.webmanifest, name="webmanifest"),
]
