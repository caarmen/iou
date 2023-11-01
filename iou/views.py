import os
from typing import Iterable

from django.forms import ChoiceField, ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from iou import service
from iou.models import Debt, Person
from iou.templatetags.iou_filters import person
from iou.widgets import ButtonSelect


class DebtForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs["placeholder"] = _("hint_amount")
        self.fields["description"].widget.attrs["placeholder"] = _("hint_description")
        self.fields["description"].label = _("label_description")

    debtor = ChoiceField(
        choices=(
            (Person.PERSON_1, os.getenv("PERSON_1_NAME", "Person 1")),
            (Person.PERSON_2, os.getenv("PERSON_2_NAME", "Person 2")),
        ),
        widget=ButtonSelect,
        label=False,
    )

    class Meta:
        model = Debt
        fields = ["amount", "description", "debtor"]
        required_fields = ["amount", "debtor"]


def index(request: HttpRequest):
    if request.method == "POST":
        form = DebtForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("index"))

    latest_debts: Iterable[Debt] = Debt.objects.order_by("-created_at")[0:5]
    latest_debts_text = [
        _("debt_list_item_with_description").format(
            person(debt.debtor),
            debt.amount,
            debt.description,
        )
        if debt.description
        else _("debt_list_item").format(
            person(debt.debtor),
            debt.amount,
        )
        for debt in latest_debts
    ]
    debtor_debt = service.get_debtor_debt()
    debtor_debt_text = (
        _("who_owes_what").format(person(debtor_debt.debtor), debtor_debt.amount)
        if debtor_debt
        else None
    )
    form = DebtForm(
        label_suffix="",
    )
    context = {
        "latest_debts_text": latest_debts_text,
        "debtor_debt_text": debtor_debt_text,
        "form": form,
    }
    return render(request, "iou/index.html", context)
