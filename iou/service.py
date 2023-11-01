import dataclasses
from decimal import Decimal

from django.db.models import Sum

from iou.models import Debt, Person


@dataclasses.dataclass
class NetDebt:
    debtor: Person
    amount: float


def get_net_debt() -> NetDebt | None:
    debts = (
        Debt.objects.values("debtor")
        .annotate(total_debt=Sum("amount"))
        .order_by("-total_debt")
    )
    if len(debts) == 1:
        return NetDebt(debtor=debts[0]["debtor"], amount=debts[0]["total_debt"])

    if len(debts) == 2:
        net_debt = Decimal(debts[0]["total_debt"] - debts[1]["total_debt"])
        if net_debt:
            return NetDebt(
                debtor=debts[0]["debtor"],
                amount=debts[0]["total_debt"] - debts[1]["total_debt"],
            )

    return None


def get_latest_debts() -> list[Debt]:
    return Debt.objects.order_by("-created_at")[0:5]
