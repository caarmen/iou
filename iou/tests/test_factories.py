import datetime
from decimal import Decimal

import pytest

from iou.models import Debt, Person
from iou.tests.factories import DebtFactory


@pytest.mark.django_db
def test_debt_factory(
    debt_factory: DebtFactory,
):
    debt: Debt = debt_factory()
    assert isinstance(debt.id, int)
    assert isinstance(debt.debtor, Person)
    assert isinstance(debt.amount, Decimal)
    assert isinstance(debt.description, str)
    assert isinstance(debt.created_at, datetime.datetime)
