import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture()
def test_account_password():
    return "secret"


@pytest.fixture()
def user(test_account_password):
    return User.objects.create_user(username="fred", password=test_account_password)


@pytest.fixture()
def client(user: User, test_account_password: str):
    c = Client()
    c.login(username=user.username, password=test_account_password)
    return c
