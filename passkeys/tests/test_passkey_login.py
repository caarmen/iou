import dataclasses
import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import Client
from django.urls import reverse
from webauthn.helpers import bytes_to_base64url

from passkeys.models import Credential

User = get_user_model()

pytestmark = pytest.mark.django_db

# The contents of credential_json aren't important, since we mock
# the webauthn verification.
# We just need credential_json to be a json object.
FAKE_CREDENTIAL_PAYLOAD = {
    "credential_json": json.dumps(
        {
            "foo": 42,
        }
    )
}


def test_passkey_login_start_authenticated(
    client: Client,
):
    """
    Given an authenticated user
    When the user accesses the route to start passkey login
    Then the user is redirected to the main page.
    """
    response = client.get(reverse("passkeys:login-start"))
    assert response.status_code == 302
    assert response.url == reverse("iou:index")


def test_passkey_login_finish_authenticated(
    client: Client,
):
    """
    Given an authenticated user
    When the user accesses the route to finish passkey login
    Then the user is redirected to the main page.
    """
    response = client.post(reverse("passkeys:login-finish"))
    assert response.status_code == 302
    assert response.url == reverse("iou:index")


@dataclasses.dataclass
class MockAuthenticatorAssertionResponse:
    user_handle: bytes | None


@dataclasses.dataclass
class MockAuthenticationCredential:
    id: str
    response: MockAuthenticatorAssertionResponse


@dataclasses.dataclass
class MockVerifiedAuthentication:
    user_verified: bool
    new_sign_count: int


def test_passkey_login(
    user: AbstractUser,
):
    """
    Given an unauthenticated user with a credential,
    When the user chooses to log in with a passkey
    Then the the flow completes successfully
    And the user is redirected to the main page.
    """

    fake_cred_id = b"some cred id"
    fake_cred_public_key = b"some public key"
    Credential.objects.create(
        user=user,
        credential_id=bytes_to_base64url(fake_cred_id),
        public_key=bytes_to_base64url(fake_cred_public_key),
    )
    assert Credential.objects.count() == 1

    # Step 1: start the login flow.
    client = Client()
    response_start = client.get(reverse("passkeys:login-start"))
    assert response_start.status_code == 200

    # Step 2: complete the login flow.
    with patch(
        "passkeys.views.parse_authentication_credential_json"
    ) as mock_parse_credential_json, patch(
        "passkeys.views.verify_authentication_response"
    ) as mock_verify_auth_response:
        mock_parse_credential_json.return_value = MockAuthenticationCredential(
            id=bytes_to_base64url(fake_cred_id),
            response=MockAuthenticatorAssertionResponse(
                user_handle=user.uuid.bytes,
            ),
        )

        mock_verify_auth_response.return_value = MockVerifiedAuthentication(
            user_verified=True,
            new_sign_count=0,
        )

        response_finish = client.post(
            reverse("passkeys:login-finish"),
            FAKE_CREDENTIAL_PAYLOAD,
        )

    # Verify that no new credential was created.
    assert Credential.objects.count() == 1
    credential = Credential.objects.first()

    # Verify the attributes of the credential.
    assert credential.user == user
    assert credential.credential_id == bytes_to_base64url(fake_cred_id)
    assert credential.sign_count == 0

    # Verify that we're logged into the main page.
    assert response_finish.status_code == 302
    assert response_finish.url == reverse("iou:index")


def test_passkey_login_no_matching_credential(user):
    """
    Given an unauthenticated user,
    When the user accesses the passkey login finish route,
    And the credential doesn't match any credential in the db,
    Then the expected error is returned.
    """

    assert Credential.objects.count() == 0

    client = Client()
    with patch(
        "passkeys.views.parse_authentication_credential_json"
    ) as mock_parse_credential_json:
        mock_parse_credential_json.return_value = MockAuthenticationCredential(
            id=bytes_to_base64url(b"some cred id we don't know about"),
            response=MockAuthenticatorAssertionResponse(
                user_handle=user.uuid.bytes,
            ),
        )

        response_finish = client.post(
            reverse("passkeys:login-finish"),
            FAKE_CREDENTIAL_PAYLOAD,
        )

    assert Credential.objects.count() == 0
    assert response_finish.status_code == 400


def test_passkey_login_no_user_handle(user):
    """
    Given an unauthenticated user,
    When the user attempts to use the passkey login finish route,
    And the credential has no user handle
    Then the expected error is returned.
    """
    fake_cred_id = b"some cred id"
    fake_cred_public_key = b"some public key"
    Credential.objects.create(
        user=user,
        credential_id=bytes_to_base64url(fake_cred_id),
        public_key=bytes_to_base64url(fake_cred_public_key),
    )
    assert Credential.objects.count() == 1

    client = Client()
    with patch(
        "passkeys.views.parse_authentication_credential_json"
    ) as mock_parse_credential_json, patch(
        "passkeys.views.verify_authentication_response"
    ) as mock_verify_auth_response:
        mock_parse_credential_json.return_value = MockAuthenticationCredential(
            id=bytes_to_base64url(fake_cred_id),
            response=MockAuthenticatorAssertionResponse(
                user_handle=None,
            ),
        )

        mock_verify_auth_response.return_value = MockVerifiedAuthentication(
            user_verified=True,
            new_sign_count=0,
        )

        response_finish = client.post(
            reverse("passkeys:login-finish"),
            FAKE_CREDENTIAL_PAYLOAD,
        )

    assert Credential.objects.count() == 1
    assert response_finish.status_code == 400


def test_passkey_login_user_not_verified(user):
    """
    Given an unauthenticated user,
    When the user attempts to use the passkey login finish route,
    And the user is flagged as not verified,
    Then the expected error is returned.
    """
    fake_cred_id = b"some cred id"
    fake_cred_public_key = b"some public key"
    Credential.objects.create(
        user=user,
        credential_id=bytes_to_base64url(fake_cred_id),
        public_key=bytes_to_base64url(fake_cred_public_key),
    )
    assert Credential.objects.count() == 1

    client = Client()
    with patch(
        "passkeys.views.parse_authentication_credential_json"
    ) as mock_parse_credential_json, patch(
        "passkeys.views.verify_authentication_response"
    ) as mock_verify_auth_response:
        mock_parse_credential_json.return_value = MockAuthenticationCredential(
            id=bytes_to_base64url(fake_cred_id),
            response=MockAuthenticatorAssertionResponse(
                user_handle=user.uuid.bytes,
            ),
        )

        mock_verify_auth_response.return_value = MockVerifiedAuthentication(
            user_verified=False,
            new_sign_count=0,
        )

        response_finish = client.post(
            reverse("passkeys:login-finish"),
            FAKE_CREDENTIAL_PAYLOAD,
        )

    assert Credential.objects.count() == 1
    assert response_finish.status_code == 400


def test_passkey_login_wrong_user():
    """
    Given two unauthenticated users user1 and user2,
    When a user attempts to use the passkey login finish route,
    And the client's credential id matches user1,
    And the client's user handle matches user2,
    Then the expected error is returned.
    """
    user1 = User.objects.create_user(username="jdoe", password="password1")
    user2 = User.objects.create_user(username="mduval", password="password2")

    user1_cred_id = b"user 1 cred id"
    user1_public_key = b"user 1 public key"
    Credential.objects.create(
        user=user1,
        credential_id=bytes_to_base64url(user1_cred_id),
        public_key=bytes_to_base64url(user1_public_key),
    )
    assert Credential.objects.count() == 1

    client = Client()
    with patch(
        "passkeys.views.parse_authentication_credential_json"
    ) as mock_parse_credential_json, patch(
        "passkeys.views.verify_authentication_response"
    ) as mock_verify_auth_response:
        mock_parse_credential_json.return_value = MockAuthenticationCredential(
            id=bytes_to_base64url(user1_cred_id),
            response=MockAuthenticatorAssertionResponse(
                user_handle=user2.uuid.bytes,
            ),
        )

        mock_verify_auth_response.return_value = MockVerifiedAuthentication(
            user_verified=True,
            new_sign_count=0,
        )

        response_finish = client.post(
            reverse("passkeys:login-finish"),
            FAKE_CREDENTIAL_PAYLOAD,
        )

    assert Credential.objects.count() == 1
    assert response_finish.status_code == 400
