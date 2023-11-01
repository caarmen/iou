from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from iou import service
from iou.forms import DebtForm
from iou.templatetags import iou_filters


def index(request: HttpRequest):
    if request.method == "POST":
        form = DebtForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("index"))

    return render(
        request=request,
        template_name="iou/index.html",
        context={
            "latest_debts_text": [
                iou_filters.debt(x) for x in service.get_latest_debts()
            ],
            "net_debt_text": iou_filters.net_debt(
                service.get_net_debt(),
            ),
            "form": DebtForm(label_suffix=""),
        },
    )
