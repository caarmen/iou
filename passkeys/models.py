from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Credential(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    credential_id = models.CharField(
        max_length=1024,
        unique=True,
    )
    public_key = models.TextField()
    sign_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
