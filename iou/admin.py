import os

from django.contrib import admin

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
                (Person.PERSON_1, os.getenv("PERSON_1_NAME", "Person 1")),
                (Person.PERSON_2, os.getenv("PERSON_2_NAME", "Person 2")),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_debtor_display(self, obj: Debt) -> str | None:
        if obj.debtor == Person.PERSON_1:
            return os.environ["PERSON_1_NAME"]
        if obj.debtor == Person.PERSON_2:
            return os.environ["PERSON_2_NAME"]
        return obj.debtor

    get_debtor_display.short_description = Debt.debtor.field.verbose_name

    def has_change_permission(self, request, obj=None):
        return False  # Disable the ability to change existing objects


admin.site.register(Debt, DebtAdmin)
