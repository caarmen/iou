from django.forms.widgets import ChoiceWidget


class ButtonSelect(ChoiceWidget):
    template_name = "django/forms/widgets/multiple_input.html"
    option_template_name = "iou/form_button.html"
