from decimal import Decimal
from typing import Iterable

import pytest
from django.test import Client

from iou.forms import DebtForm
from iou.models import Debt, Person
from iou.service import NetDebt
from iou.tests.factories import DebtFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    ids=["min", "max", "step"],
    argnames=["attr_name", "expected_value"],
    argvalues=[
        ["min", 0.01],
        ["max", 999999.99],
        ["step", "0.01"],
    ],
)
def test_form_amount_widget_attrs(attr_name, expected_value):
    form = DebtForm()
    assert form.fields["amount"].widget.attrs[attr_name] == expected_value


@pytest.mark.django_db
def test_list_debts(
    client: Client,
    debt_factory: DebtFactory,
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

    response = client.get("/iou/")
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
    response = client.get("/iou/")
    assert response.status_code == 200
    latest_debts: Iterable[Debt] = response.context["latest_debts"]
    assert len(latest_debts) == 0

    net_debt: NetDebt = response.context["net_debt"]
    assert net_debt is None


@pytest.mark.django_db
def test_net_debt_zero(
    client: Client,
    debt_factory: DebtFactory,
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

    response = client.get("/iou/")
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

    response = client.post("/iou/", client_input)

    assert response.status_code == 302
    assert response.url == "/iou/"

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

    response = client.post("/iou/", client_input)

    assert response.status_code == 400
    response_json: dict = response.json()
    for expected_error_key in expected_error_keys:
        assert expected_error_key in response_json

    debts = Debt.objects.all()
    assert debts.count() == 0
