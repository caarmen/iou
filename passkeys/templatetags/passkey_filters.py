from django import template
from django.contrib.humanize.templatetags import humanize
from django.utils.translation import gettext_lazy as _

from passkeys.models import Credential

register = template.Library()


@register.filter(name="passkey_last_used")
def passkey_last_used(
    value: Credential,
) -> str:
    if value.last_used_at:
        return humanize.naturaltime(value.last_used_at)
    return _("passkey_never")
