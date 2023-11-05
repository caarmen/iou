from django.forms import ChoiceField, ModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from formtools.preview import FormPreview

from iou.formatters import person
from iou.models import Debt, Person
from iou.widgets import ButtonSelect


class DebtForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs["placeholder"] = _("hint_amount")
        self.fields["description"].widget.attrs["placeholder"] = _("hint_description")
        for field in self.fields.values():
            field.label = ""

    debtor = ChoiceField(
        choices=(
            (Person.PERSON_1, person(Person.PERSON_1)),
            (Person.PERSON_2, person(Person.PERSON_2)),
        ),
        widget=ButtonSelect,
    )

    class Meta:
        model = Debt
        fields = ["amount", "description", "debtor"]
        required_fields = ["amount", "debtor"]


class DebtFormPreview(FormPreview):
    form_template = "iou/index.html"

    def done(self, request, cleaned_data):
        return HttpResponseRedirect(reverse("index"))
