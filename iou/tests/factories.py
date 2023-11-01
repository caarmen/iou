from factory import Faker
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from pytest_factoryboy import register

from iou.models import Debt, Person


@register
class DebtFactory(DjangoModelFactory):
    debtor = FuzzyChoice(choices=Person)
    description = Faker("pystr")
    amount = FuzzyDecimal(0, 1000, 2)

    class Meta:
        model = Debt
