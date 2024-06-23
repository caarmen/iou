import datetime
from decimal import Decimal

import pytest

from iou.models import Debt, Person
from iou.tests.factories import DebtFactory
from iou.tests.fixtures import MockSlackRequest


@pytest.mark.django_db
def test_debt_factory(
    debt_factory: DebtFactory,
    mock_slack_request: MockSlackRequest,
):
    debt: Debt = debt_factory()
    assert isinstance(debt.id, int)
    assert isinstance(debt.debtor, Person)
    assert isinstance(debt.amount, Decimal)
    assert isinstance(debt.description, str)
    assert isinstance(debt.created_at, datetime.datetime)

    expected_slack_request_call_count = (
        1 if mock_slack_request.is_slack_configured else 0
    )
    assert mock_slack_request.request.call_count == expected_slack_request_call_count
