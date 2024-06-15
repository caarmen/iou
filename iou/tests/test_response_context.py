from decimal import Decimal
from typing import Iterable

import pytest
from django.test import Client
from django.urls import reverse

from iou.models import Debt, Person
from iou.service import NetDebt
from iou.tests.factories import DebtFactory
from iou.tests.fixtures import MockSlackRequest


@pytest.mark.django_db
def test_list_debts(
    client: Client,
    debt_factory: DebtFactory,
    mock_slack_request: MockSlackRequest,
):
    """
    Given some debts
    And a non-zero net debt
    When the page is loaded
    Then the list of debts is present with expected values
    And the net debt is present with expected values.
    """
    debt_factory(debtor=Person.PERSON_1, amount=4.33)
    debt_factory(debtor=Person.PERSON_1, amount=5.0)
    debt_factory(debtor=Person.PERSON_2, amount=7.5, description=None)

    response = client.get(reverse("index"))
    assert response.status_code == 200
    latest_debts: Iterable[Debt] = response.context["latest_debts"]

    assert len(latest_debts) == 3

    assert latest_debts[0].amount == pytest.approx(Decimal(7.5))
    assert latest_debts[0].debtor == Person.PERSON_2
    assert latest_debts[0].description is None

    assert latest_debts[1].amount == pytest.approx(Decimal(5))
    assert latest_debts[1].debtor == Person.PERSON_1
    assert len(latest_debts[1].description) > 0

    assert latest_debts[2].amount == pytest.approx(Decimal(4.33))
    assert latest_debts[2].debtor == Person.PERSON_1
    assert len(latest_debts[2].description) > 0

    net_debt: NetDebt = response.context["net_debt"]
    assert net_debt.amount == pytest.approx(Decimal(1.83))
    assert net_debt.debtor == Person.PERSON_1

    # 3 factory debt creations
    expected_slack_request_call_count = (
        3 if mock_slack_request.is_slack_configured else 0
    )
    assert mock_slack_request.request.call_count == expected_slack_request_call_count


@pytest.mark.django_db
def test_no_debts(
    client: Client,
):
    """
    Given no debts
    When the page is loaded
    Then the list of debts is empty
    And the net debt is None.
    """
    response = client.get(reverse("index"))
    assert response.status_code == 200
    latest_debts: Iterable[Debt] = response.context["latest_debts"]
    assert len(latest_debts) == 0

    net_debt: NetDebt = response.context["net_debt"]
    assert net_debt is None


@pytest.mark.django_db
def test_net_debt_zero(
    client: Client,
    debt_factory: DebtFactory,
    mock_slack_request: MockSlackRequest,
):
    """
    Given some debts
    And a zero net debt
    When the page is loaded
    Then the list of debts is present with expected values
    And the net debt is None.
    """
    debt_factory(debtor=Person.PERSON_1, amount=4.33)
    debt_factory(debtor=Person.PERSON_1, amount=5.0)
    debt_factory(debtor=Person.PERSON_2, amount=9.33, description=None)

    response = client.get(reverse("index"))
    assert response.status_code == 200
    latest_debts: Iterable[Debt] = response.context["latest_debts"]

    assert len(latest_debts) == 3
    assert latest_debts[0].amount == pytest.approx(Decimal(9.33))
    assert latest_debts[0].debtor == Person.PERSON_2
    assert latest_debts[0].description is None

    assert latest_debts[1].amount == pytest.approx(Decimal(5))
    assert latest_debts[1].debtor == Person.PERSON_1
    assert len(latest_debts[1].description) > 0

    assert latest_debts[2].amount == pytest.approx(Decimal(4.33))
    assert latest_debts[2].debtor == Person.PERSON_1
    assert len(latest_debts[2].description) > 0

    net_debt: NetDebt = response.context["net_debt"]
    assert net_debt is None

    # 3 factory debt creations
    expected_slack_request_call_count = (
        3 if mock_slack_request.is_slack_configured else 0
    )
    assert mock_slack_request.request.call_count == expected_slack_request_call_count
