from django.db.models import QuerySet

from passkeys.models import Credential


def get_user_credentials(user) -> QuerySet[Credential]:
    return Credential.objects.filter(user=user).order_by("-created_at")
