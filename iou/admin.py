from django.contrib import admin

from iou.formatters import person
from iou.models import Debt, Person


class DebtAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_debtor_display",
        "amount",
        "description",
        "created_at",
    )

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "debtor":
            kwargs["choices"] = (
                (Person.PERSON_1, person(Person.PERSON_1)),
                (Person.PERSON_2, person(Person.PERSON_2)),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_debtor_display(self, obj: Debt) -> str | None:
        return person(obj.debtor)

    get_debtor_display.short_description = Debt.debtor.field.verbose_name


admin.site.register(Debt, DebtAdmin)
