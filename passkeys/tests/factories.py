from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from pytest_factoryboy import register

from iou.tests.factories import UserFactory
from passkeys.models import Credential


@register
class CredentialFactory(DjangoModelFactory):
    credential_id = Faker("pystr")
    public_key = Faker("pystr")
    sign_count = 0
    last_used_at = None
    user = SubFactory(UserFactory)

    class Meta:
        model = Credential
