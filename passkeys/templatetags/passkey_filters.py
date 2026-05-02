from django import template
from django.contrib.humanize.templatetags import humanize
from django.utils import formats
from django.utils.translation import gettext_lazy as _

from passkeys.models import Credential

register = template.Library()


@register.filter(name="passkey_delete_confirm_message")
def passkey_delete_confirm_message(
    value: Credential,
) -> str:
    return _("passkey_delete_confirm_message").format(
        formats.date_format(value.created_at, "SHORT_DATETIME_FORMAT"),
        (
            humanize.naturaltime(value.last_used_at)
            if value.last_used_at
            else _("passkey_never_used")
        ),
    )


@register.filter(name="passkey_last_used")
def passkey_last_used(
    value: Credential,
) -> str:
    if value.last_used_at:
        return humanize.naturaltime(value.last_used_at)
    return _("passkey_never")
