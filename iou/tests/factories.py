from uuid import uuid4

from factory import Faker, LazyFunction
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from pytest_factoryboy import register

from iou.models import Debt, Person, User


@register
class UserFactory(DjangoModelFactory):
    uuid = LazyFunction(uuid4)
    username = Faker("user_name")

    class Meta:
        model = User


@register
class DebtFactory(DjangoModelFactory):
    debtor = FuzzyChoice(choices=Person)
    description = Faker("pystr")
    amount = FuzzyDecimal(0, 1000, 2)

    class Meta:
        model = Debt
