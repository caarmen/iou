import os

from django import template

from iou.models import Person

register = template.Library()


@register.filter(name="person")
def person(value):
    if value == Person.PERSON_1:
        return os.environ["PERSON_1_NAME"]
    if value == Person.PERSON_2:
        return os.environ["PERSON_2_NAME"]
    return value
