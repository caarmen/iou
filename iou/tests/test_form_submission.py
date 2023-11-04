from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from iou.models import Debt, Person


@pytest.mark.parametrize(
    ids=["full data", "required data", "empty_description"],
    argnames=[
        "client_input",
        "expected_debtor",
        "expected_amount",
        "expected_description",
    ],
    argvalues=[
        [
            {
                "debtor": Person.PERSON_1,
                "amount": 42.3,
                "description": "movie tickets",
            },
            Person.PERSON_1,
            42.3,
            "movie tickets",
        ],
        [
            {
                "debtor": Person.PERSON_1,
                "amount": 42.3,
            },
            Person.PERSON_1,
            42.3,
            None,
        ],
        [
            {
                "debtor": Person.PERSON_1,
                "amount": 42.3,
                "description": "",
            },
            Person.PERSON_1,
            42.3,
            None,
        ],
    ],
)
@pytest.mark.django_db
def test_add_debt(
    client: Client,
    client_input: dict,
    expected_debtor: Person,
    expected_amount: float,
    expected_description: str | None,
):
    """
    When a client submits the form to create a Debt entry
    Then the form is submitted successfully
    And the Debt object is created.
    """
    debts = Debt.objects.all()
    assert debts.count() == 0

    response = client.post(reverse("index"), client_input)

    assert response.status_code == 302
    assert response.url == reverse("index")

    debts = Debt.objects.all()
    assert debts.count() == 1

    debt = debts[0]
    assert debt.debtor == expected_debtor
    assert debt.amount == pytest.approx(Decimal(expected_amount))
    assert debt.description == expected_description


@pytest.mark.parametrize(
    ids=[
        "missing_debtor",
        "missing_amount",
        "empty_input",
        "string_amount",
        "negative_amount",
        "unknown_debtor",
    ],
    argnames=[
        "client_input",
        "expected_error_keys",
    ],
    argvalues=[
        [
            {
                "amount": 42.3,
                "description": "movie tickets",
            },
            ["debtor"],
        ],
        [
            {
                "debtor": Person.PERSON_2,
                "description": "movie tickets",
            },
            ["amount"],
        ],
        [
            {},
            ["amount", "debtor"],
        ],
        [
            {
                "debtor": Person.PERSON_2,
                "amount": "hello there",
            },
            ["amount"],
        ],
        [
            {
                "debtor": Person.PERSON_2,
                "amount": -3.2,
            },
            ["amount"],
        ],
        [
            {
                "debtor": "Bob",
                "amount": 5.2,
            },
            ["debtor"],
        ],
    ],
)
@pytest.mark.django_db
def test_invalid_input(
    client: Client,
    client_input: dict,
    expected_error_keys: list[str],
):
    """
    When a client submits a form with invalid data to create a Debt,
    Then an expected error is returned
    And no Debt is created.
    """
    debts = Debt.objects.all()
    assert debts.count() == 0

    response = client.post(reverse("index"), client_input)

    assert response.status_code == 400
    response_json: dict = response.json()
    for expected_error_key in expected_error_keys:
        assert expected_error_key in response_json

    debts = Debt.objects.all()
    assert debts.count() == 0
