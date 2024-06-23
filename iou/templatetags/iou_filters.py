from django import template
from django.contrib.auth.models import User
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


@register.filter(name="user")
def user(value: User) -> str:
    if not value:
        return _("no_user")
    if value.is_anonymous:
        return _("anonymous_user")
    username = value.username.strip()
    if not username:
        return _("unknown_user")
    return username


@register.filter(name="bold")
def bold(value: str) -> str | None:
    if not value:
        return None
    return f"*{value}*"
