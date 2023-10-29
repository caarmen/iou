import os

from django.forms import ChoiceField, ModelForm, RadioSelect
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from iou import service
from iou.models import Debt, Person
from iou.templatetags.iou_filters import person


class DebtForm(ModelForm):
    debtor = ChoiceField(
        choices=(
            (Person.PERSON_1, os.getenv("PERSON_1_NAME", "Person 1")),
            (Person.PERSON_2, os.getenv("PERSON_2_NAME", "Person 2")),
        ),
        widget=RadioSelect,
        label=Debt.debtor.field.verbose_name,
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

    latest_debts = Debt.objects.order_by("-created_at")[0:5]
    debtor_debt = service.get_debtor_debt()
    debtor_debt_text = (
        _("who_owes_what").format(person(debtor_debt.debtor), debtor_debt.amount)
        if debtor_debt
        else None
    )
    form = DebtForm()
    context = {
        "latest_debts": latest_debts,
        "debtor_debt_text": debtor_debt_text,
        "form": form,
    }
    return render(request, "iou/index.html", context)
