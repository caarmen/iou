from django import template
from django.utils.translation import gettext_lazy as _

from iou.formatters import money, person
from iou.models import Debt
from iou.service import NetDebt

register = template.Library()


@register.filter(name="debt")
def debt(value: Debt) -> str:
    if value.description:
        return _("debt_list_item_with_description").format(
            person(value.debtor),
            money(value.amount),
            value.description,
        )

    return _("debt_list_item").format(
        person(value.debtor),
        money(value.amount),
    )


@register.filter(name="net_debt")
def net_debt(value: NetDebt) -> str:
    return (
        _("who_owes_what").format(person(value.debtor), money(value.amount))
        if value
        else ""
    )
