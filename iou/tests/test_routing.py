import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_redirect_home(
    client: Client,
):
    response = client.get("/")
    assert response.status_code == 301
    assert response.url == reverse("iou:index")
