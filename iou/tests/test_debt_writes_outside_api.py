import pytest

from iou.models import Debt, Person
from iou.tests.factories import DebtFactory
from iou.tests.fixtures import MockSlackRequest


@pytest.mark.django_db
def test_create_debt(
    debt_factory: DebtFactory,
    mock_slack_request: MockSlackRequest,
):
    """
    When a debt is created
    Then a message is sent to slack as expected.
    """
    assert mock_slack_request.request.call_count == 0
    assert Debt.objects.count() == 0

    debt_factory(amount=5.0, debtor=Person.PERSON_1)
    assert Debt.objects.count() == 1

    assert mock_slack_request.request.call_count == (
        1 if mock_slack_request.is_slack_configured else 0
    )


@pytest.mark.django_db
def test_modify_debt(
    debt_factory: DebtFactory,
    mock_slack_request: MockSlackRequest,
):
    """
    When a debt is modified
    Then a message is sent to slack as expected.
    """
    debt: Debt = debt_factory(amount=5.0, debtor=Person.PERSON_1)

    # Don't care about messages sent during test fixture setup.
    mock_slack_request.request.reset()
    debt.amount = 6.0
    debt.save()
    debt.refresh_from_db()
    assert debt.amount == pytest.approx(6.0)

    assert mock_slack_request.request.call_count == (
        1 if mock_slack_request.is_slack_configured else 0
    )


@pytest.mark.django_db
def test_delete_debt(
    debt_factory: DebtFactory,
    mock_slack_request: MockSlackRequest,
):
    """
    When a debt is deleted
    Then a message is sent to slack as expected.
    """
    debt: Debt = debt_factory(amount=5.0, debtor=Person.PERSON_1)
    assert Debt.objects.count() == 1

    # Don't care about messages sent during test fixture setup.
    mock_slack_request.request.reset()

    debt.delete()
    assert Debt.objects.count() == 0

    assert mock_slack_request.request.call_count == (
        1 if mock_slack_request.is_slack_configured else 0
    )
