import os
from decimal import Decimal

from babel.numbers import format_compact_currency
from django.utils.translation import get_language, to_locale

from iou.models import Person


def person(person: Person) -> str:
    if person == Person.PERSON_1:
        return os.environ["PERSON_1_NAME"]
    if person == Person.PERSON_2:
        return os.environ["PERSON_2_NAME"]
    return person


def money(amount: Decimal) -> str:
    return format_compact_currency(
        number=amount,
        currency=os.environ["CURRENCY_CODE"],
        locale=to_locale(get_language()),
        fraction_digits=2,
    )
