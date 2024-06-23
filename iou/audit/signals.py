import logging
import os

import requests
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from iou import service
from iou.decorators import ensure_envvar_set
from iou.middlewares import CurrentUserMiddleware
from iou.models import Debt

logger = logging.getLogger(__file__)

# Preload these translation strings.
# Not really for perf: but so that `django-admin makemessages`
# can find them and add them to the django.po files.
audit_debt_created = _("audit_debt_created")
audit_debt_modified = _("audit_debt_modified")
audit_debt_deleted = _("audit_debt_deleted")


@receiver(post_save, sender=Debt, dispatch_uid="audit_on_debt_created")
@ensure_envvar_set("SLACK_WEBHOOK")
def on_debt_created(sender, instance, created, **kwargs):
    """
    Post a message to slack when a Debt object is created.
    """
    _on_debt_event(
        audit_debt_event_title=audit_debt_created if created else audit_debt_modified,
        debt=instance,
    )


@receiver(post_delete, sender=Debt, dispatch_uid="audit_on_debt_deleted")
@ensure_envvar_set("SLACK_WEBHOOK")
def on_debt_deleted(sender, instance, **kwargs):
    """
    Post a message to slack when a Debt object is deleted.
    """
    _on_debt_event(
        audit_debt_event_title=audit_debt_deleted,
        debt=instance,
    )


def _on_debt_event(audit_debt_event_title: str, debt: Debt):
    try:
        message = _create_audit_message(
            user=CurrentUserMiddleware.get_current_user(),
            audit_debt_event_title=audit_debt_event_title,
            debt=debt,
        )
        _post_audit_message(message)
    except Exception as e:
        logger.warn("Error auditing debt event %s: %s", audit_debt_event_title, e)


def _create_audit_message(
    user: User,
    audit_debt_event_title: str,
    debt: Debt,
) -> str:
    return render_to_string(
        template_name="audit_debt_event.txt",
        context={
            "user": user,
            "audit_debt_event_title": audit_debt_event_title,
            "debt": debt,
            "latest_debts": service.get_latest_debts(),
            "net_debt": service.get_net_debt(),
        },
        using="jinja2",
    )


def _post_audit_message(message: str) -> None:
    SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
    requests.post(SLACK_WEBHOOK, json={"text": message})
