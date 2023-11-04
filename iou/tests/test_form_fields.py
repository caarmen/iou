import pytest

from iou.forms import DebtForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    ids=["min", "max", "step"],
    argnames=["attr_name", "expected_value"],
    argvalues=[
        ["min", 0.01],
        ["max", 999999.99],
        ["step", "0.01"],
    ],
)
def test_form_amount_widget_attrs(attr_name, expected_value):
    """
    Validate that the amount form field has the expected widget attributes
    """
    form = DebtForm()
    assert form.fields["amount"].widget.attrs[attr_name] == expected_value
