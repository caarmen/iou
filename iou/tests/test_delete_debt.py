from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from iou.models import Debt, Person
from iou.tests.factories import DebtFactory


@pytest.mark.django_db
def test_delete_debt_success(
    client: Client,
    debt_factory: DebtFactory,
):
    """
    When a client submits the form to delete an existing Debt entry
    Then the form is submitted successfully
    And the Debt object is deleted
    """
    debts = Debt.objects.all()
    assert debts.count() == 0

    debt_factory(amount=5.0, debtor=Person.PERSON_1)
    debt_factory(amount=4.0, debtor=Person.PERSON_2)

    response = client.post(reverse("delete", kwargs={"debt_id": 2}))

    assert response.status_code == 302
    assert response.url == reverse("index")

    debts = Debt.objects.all()
    assert debts.count() == 1

    debt = debts[0]
    assert debt.debtor == Person.PERSON_1
    assert debt.amount == pytest.approx(Decimal(5.0))


@pytest.mark.django_db
def test_delete_unknown_debt_fail(
    client: Client,
    debt_factory: DebtFactory,
):
    """
    When a client submits the form to delete an inalid Debt entry
    Then the form is submitted with an expected error
    And no Debt object are deleted
    """
    debts = Debt.objects.all()
    assert debts.count() == 0

    debt_factory(amount=5.0, debtor=Person.PERSON_1)
    debt_factory(amount=4.0, debtor=Person.PERSON_2)

    response = client.post(reverse("delete", kwargs={"debt_id": 3}))

    assert response.status_code == 404

    debts = Debt.objects.all()
    assert debts.count() == 2
