from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from iou import service
from iou.forms import DebtForm
from iou.models import Debt


@login_required
def index(request: HttpRequest):
    if request.method == "POST":
        form = DebtForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            # If we get here, it's because the user is bypassing our form
            return JsonResponse(form.errors, status=400)

    return render(
        request=request,
        template_name="iou/index.html",
        context={
            "latest_debts": service.get_latest_debts(),
            "net_debt": service.get_net_debt(),
            "form": DebtForm(),
        },
    )


@login_required
def delete(request: HttpRequest, debt_id):
    if request.method == "POST":
        get_object_or_404(Debt, id=debt_id).delete()
    return render(
        request,
        template_name="iou/partials/debt_list.html",
        context={
            "latest_debts": service.get_latest_debts(),
            "net_debt": service.get_net_debt(),
        },
    )


def webmanifest(request: HttpRequest):
    return render(request, template_name="iou/site.webmanifest")
