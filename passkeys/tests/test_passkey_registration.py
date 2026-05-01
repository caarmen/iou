import dataclasses
import json
from unittest.mock import patch

import pytest
from django.contrib.auth.models import AbstractUser
from django.test import Client
from django.urls import reverse
from webauthn.helpers import bytes_to_base64url

from passkeys.models import Credential

pytestmark = pytest.mark.django_db


def test_passkey_register_start_unauthenticated():
    """
    Given an unauthenticated user
    When the user accesses the route to start passkey registration
    Then the user is redirected to login.
    """
    client = Client()
    response = client.get(reverse("passkeys:index"))
    assert response.status_code == 302
    assert (
        response.url
        == f"{reverse('passkeys:login-start')}?next={reverse('passkeys:index')}"
    )


def test_passkey_register_finish_unauthenticated():
    """
    Given an unauthenticated user
    When the user accesses the route to finish passkey registration
    Then the user is redirected to login.
    """
    client = Client()
    response = client.post(reverse("passkeys:register-finish"))
    assert response.status_code == 302
    assert (
        response.url
        == f"{reverse('passkeys:login-start')}?next={reverse('passkeys:register-finish')}"
    )


@dataclasses.dataclass
class MockVerifiedRegistration:
    credential_id: bytes
    credential_public_key: bytes


def test_passkey_register(
    user: AbstractUser,
    client: Client,
):
    """
    Given an authenticated user,
    When the user registers a new passkey,
    Then the new passkey is successfully created.
    """

    assert Credential.objects.count() == 0

    # Step 1: start the registration flow.
    response_start = client.get(reverse("passkeys:index"))
    assert response_start.status_code == 200

    # Check that the registration flow contains attributes for the user.
    context_options = response_start.context["options"]
    assert context_options["user"]["displayName"] == user.username

    # Step 2: complete the registration flow.
    fake_cred_id = b"some cred id"
    fake_cred_public_key = b"some public key"
    with patch("passkeys.views.verify_registration_response") as mock_webauthn_verify:
        mock_webauthn_verify.return_value = MockVerifiedRegistration(
            credential_id=fake_cred_id,
            credential_public_key=fake_cred_public_key,
        )

        response_finish = client.post(
            reverse("passkeys:register-finish"),
            {
                # The contents of credential_json aren't important, since we mock
                # the webauthn verification.
                # We just need credential_json to be a json object.
                "credential_json": json.dumps(
                    {
                        "foo": 42,
                    }
                )
            },
        )

    # Verify that the credential was created.
    assert Credential.objects.count() == 1
    created_credential = Credential.objects.first()
    assert created_credential.user == user
    assert created_credential.credential_id == bytes_to_base64url(fake_cred_id)
    assert created_credential.sign_count == 0
    assert response_finish.status_code == 200
