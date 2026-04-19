import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from webauthn import (
    base64url_to_bytes,
    generate_registration_options,
    verify_registration_response,
)
from webauthn.helpers import (
    bytes_to_base64url,
    options_to_json_dict,
)

from passkeys.models import Credential

User = get_user_model()

SESSION_KEY_CHALLENGE = "challenge"
WEBAUTHN_RP_NAME = "IOU"


@require_GET
@login_required
def register_start(request: HttpRequest):
    user = request.user
    # https://github.com/duo-labs/py_webauthn/blob/master/examples/registration.py
    registration_options = generate_registration_options(
        rp_id=request.get_host().split(":")[0],
        rp_name=WEBAUTHN_RP_NAME,
        user_name=user.username,
        user_id=user.uuid.bytes,
    )
    options_dict = options_to_json_dict(registration_options)
    request.session[SESSION_KEY_CHALLENGE] = options_dict["challenge"]
    return render(
        request,
        context={
            "options": options_dict,
        },
        template_name="passkeys/register_start.html",
    )


@require_POST
@login_required
def register_finish(request: HttpRequest):
    registration_verification = verify_registration_response(
        credential=json.loads(request.POST["credential_json"]),
        expected_challenge=base64url_to_bytes(
            request.session.get(SESSION_KEY_CHALLENGE)
        ),
        expected_origin=request.build_absolute_uri("/").rstrip("/"),
        expected_rp_id=request.get_host().split(":")[0],
        require_user_verification=True,
    )
    credential_public_key = bytes_to_base64url(
        registration_verification.credential_public_key
    )
    credential_id = bytes_to_base64url(registration_verification.credential_id)
    Credential.objects.create(
        user=request.user,
        public_key=credential_public_key,
        credential_id=credential_id,
    )
    return render(
        request,
        template_name="passkeys/register_finish.html",
    )
