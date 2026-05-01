import pytest
from django.test import Client
from django.urls import reverse

from iou.tests.factories import UserFactory
from passkeys.models import Credential
from passkeys.tests.factories import CredentialFactory

pytestmark = pytest.mark.django_db


def test_passkey_delete_ok(
    client: Client,
    user,
    credential_factory: CredentialFactory,
):
    """
    Given an authenticated user,
    When the user submits the form to delete a credential they own,
    Then the response is a success,
    And the credential is deleted,
    And the page contains only the remaining passkeys.
    """

    # Given an authenticated user (from the client fixture),
    credential1: Credential = credential_factory(user=user)
    credential2: Credential = credential_factory(user=user)

    assert Credential.objects.count() == 2

    # When the user submits the form to delete a credential they own,
    response = client.post(
        reverse("passkeys:delete", kwargs={"credential_id": credential1.credential_id})
    )

    # Then the response is a success,
    assert response.status_code == 200
    assert response.context.template_name == "passkeys/partials/passkeys_list.html"

    # And the credential is deleted.
    assert Credential.objects.count() == 1

    assert (
        Credential.objects.filter(credential_id=credential1.credential_id).count() == 0
    )
    assert (
        Credential.objects.filter(credential_id=credential2.credential_id).count() == 1
    )

    # And the page contains only the remaining passkeys.
    assert list(
        response.context["credentials"].values_list("credential_id", flat=True)
    ) == [
        credential2.credential_id,
    ]


def test_passkey_delete_unauthenticated_fail(
    user_factory: UserFactory,
    credential_factory: CredentialFactory,
):
    """
    Given an unauthenticated user,
    When the user submits the form to delete a credential they own,
    Then the response fails,
    And the credential isn't deleted.
    """

    # Given an unauthenticated user,
    user = user_factory()
    credential: Credential = credential_factory(user=user)
    assert Credential.objects.count() == 1

    # When the user submits the form to delete a credential they own,
    client = Client()
    response = client.post(
        reverse("passkeys:delete", kwargs={"credential_id": credential.credential_id})
    )

    # Then the response fails,
    assert response.status_code == 302
    assert (
        response.url
        == f"{reverse('passkeys:login-start')}?next={reverse('passkeys:delete', kwargs={'credential_id': credential.credential_id})}"
    )

    # And the credential isn't deleted.
    assert Credential.objects.count() == 1
    assert Credential.objects.first().credential_id == credential.credential_id


def test_passkey_delete_wrong_user_fail(
    client: Client,
    user_factory: UserFactory,
    credential_factory: CredentialFactory,
):
    """
    Given an authenticated user,
    When the user submits the form to delete a credential they don't own,
    Then the response fails
    And the credential isn't deleted.
    """

    # Given an authenticated user (from the client fixture),
    other_user = user_factory()
    other_user_credential: Credential = credential_factory(user=other_user)
    assert Credential.objects.count() == 1

    # When the user submits the form to delete a credential they don't own,
    response = client.post(
        reverse(
            "passkeys:delete",
            kwargs={"credential_id": other_user_credential.credential_id},
        )
    )

    # Then the response fails
    assert response.status_code == 404

    # And the credential isn't deleted.
    assert Credential.objects.count() == 1
    assert (
        Credential.objects.first().credential_id == other_user_credential.credential_id
    )
