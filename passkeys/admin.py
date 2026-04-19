from django.contrib import admin

from passkeys.models import Credential


class CredentialAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "credential_id",
        "public_key",
        "sign_count",
        "created_at",
    )


admin.site.register(Credential, CredentialAdmin)
