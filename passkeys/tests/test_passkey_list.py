import datetime as dt

import pytest
from django.test import Client
from django.urls import reverse
from freezegun import freeze_time

from iou.tests.factories import UserFactory
from passkeys.models import Credential
from passkeys.tests.factories import CredentialFactory

pytestmark = pytest.mark.django_db


def test_passkey_list_no_passkeys_ok(
    client: Client,
):
    """
    Given an authenticated user without passkeys,
    When the user loads the page to list passkeys,
    Then the response is a success,
    And the page contains no passkeys.
    """

    # Given an authenticated user (from the client fixture) without passkeys,
    assert Credential.objects.count() == 0

    # When the user loads the page to list passkeys,
    response = client.get(reverse("passkeys:index"))

    # Then the response is a success,
    assert response.status_code == 200

    # And the page contains no passkeys.
    assert response.context["credentials"].count() == 0


def test_passkey_list_some_passkeys_ok(
    user,
    client: Client,
    user_factory: UserFactory,
    credential_factory: CredentialFactory,
):
    """
    Given an authenticated user with some passkeys,
    And another user with some passkeys
    When the user loads the page to list passkeys,
    Then the response is a success,
    And the page contains all the user's passkeys in the expected order,
    And the page contains none of the other user's passkeys.
    """

    # Given an authenticated user (from the client fixture) some passkeys,
    with freeze_time(dt.datetime(2026, 3, 25, 12, 32, 45, tzinfo=dt.timezone.utc)):
        credential1 = credential_factory(
            user=user,
            last_used_at=dt.datetime(2026, 3, 25, 12, 33, 45, tzinfo=dt.timezone.utc),
        )
    with freeze_time(dt.datetime(2026, 3, 25, 12, 35, 45, tzinfo=dt.timezone.utc)):
        credential2 = credential_factory(
            user=user,
            last_used_at=None,
        )
    with freeze_time(dt.datetime(2026, 3, 25, 12, 36, 45, tzinfo=dt.timezone.utc)):
        credential3 = credential_factory(
            user=user,
            last_used_at=dt.datetime(2026, 3, 26, 12, 37, 45, tzinfo=dt.timezone.utc),
        )
    with freeze_time(dt.datetime(2026, 3, 25, 12, 38, 45, tzinfo=dt.timezone.utc)):
        credential4 = credential_factory(
            user=user,
            last_used_at=None,
        )

    # And another user with some passkeys
    other_user = user_factory()
    credential_factory(user=other_user)
    credential_factory(user=other_user)

    assert Credential.objects.count() == 6
    assert Credential.objects.filter(user=user).count() == 4

    # When the user loads the page to list passkeys,
    response = client.get(reverse("passkeys:index"))

    # Then the response is a success,
    assert response.status_code == 200

    # And the page contains all the user's passkeys in the expected order,
    # And the page contains none of the other user's passkeys.
    assert list(
        response.context["credentials"].values_list("credential_id", flat=True)
    ) == [
        credential3.credential_id,
        credential1.credential_id,
        credential4.credential_id,
        credential2.credential_id,
    ]
