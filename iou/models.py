from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class Person(models.TextChoices):
    PERSON_1 = ("P1", "Person 1")
    PERSON_2 = ("P2", "Person 2")


class Debt(models.Model):
    amount = models.DecimalField(
        verbose_name=_("model_amount_name"),
        decimal_places=2,
        max_digits=8,
        validators=[validators.MinValueValidator(0)],
        null=False,
    )

    description = models.CharField(
        verbose_name=_("model_description_name"),
        max_length=256,
        blank=True,
        null=True,
    )

    debtor = models.CharField(
        verbose_name=_("model_debtor_name"),
        max_length=2,
        choices=Person,
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(
        verbose_name=_("model_created_at_name"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("model_debt_name")
