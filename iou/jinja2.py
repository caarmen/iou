from django.contrib.humanize.templatetags import humanize
from django.utils.translation import gettext, ngettext, npgettext, pgettext
from jinja2 import Environment

from iou.templatetags.iou_filters import bold, debt, net_debt, user


def environment(**options):
    """
    Configure the jinja2 template backend.

    https://docs.djangoproject.com/en/5.0/topics/templates/#django.template.backends.jinja2.Jinja2
    """
    env = Environment(
        extensions=["jinja2.ext.i18n"],
        **options,
    )

    # Expose our custom filters:
    # https://jinja.palletsprojects.com/en/3.1.x/api/#custom-filters
    env.filters["net_debt"] = net_debt
    env.filters["debt"] = debt
    env.filters["user"] = user
    env.filters["bold"] = bold
    env.filters["naturalday"] = humanize.naturalday

    # Provide translation functions to the jinja2 engine:
    # https://jinja.palletsprojects.com/en/3.1.x/extensions/#i18n-extension
    env.globals["_"] = gettext
    env.globals["gettext"] = gettext
    env.globals["ngettext"] = ngettext
    env.globals["pgettext"] = pgettext
    env.globals["npgettext"] = npgettext

    return env
