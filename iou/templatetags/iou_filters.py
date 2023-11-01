import os

from django import template
from django.utils.translation import gettext_lazy as _

from iou.models import Debt, Person
from iou.service import NetDebt

register = template.Library()


@register.filter(name="person")
def person(value: Person) -> str:
    if value == Person.PERSON_1:
        return os.environ["PERSON_1_NAME"]
    if value == Person.PERSON_2:
        return os.environ["PERSON_2_NAME"]
    return value


@register.filter(name="debt")
def debt(value: Debt) -> str:
    if value.description:
        return _("debt_list_item_with_description").format(
            person(value.debtor),
            value.amount,
            value.description,
        )

    return _("debt_list_item").format(
        person(value.debtor),
        value.amount,
    )


@register.filter(name="net_debt")
def net_debt(value: NetDebt) -> str | None:
    return (
        _("who_owes_what").format(person(value.debtor), value.amount) if value else None
    )
