from django.urls import path

from . import views

urlpatterns = [
    # ex: /iou/
    path("", views.index, name="index"),
    path("delete/<int:debt_id>/", views.delete, name="delete"),
    path("site.webmanifest", views.webmanifest, name="webmanifest"),
]
