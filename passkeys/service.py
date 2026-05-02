from django.db.models import F, QuerySet

from passkeys.models import Credential


def get_user_credentials(user) -> QuerySet[Credential]:
    # https://docs.djangoproject.com/en/6.0/ref/models/expressions/#using-f-to-sort-null-values
    return Credential.objects.filter(user=user).order_by(
        F("last_used_at").desc(nulls_last=True),
        "-created_at",
    )
