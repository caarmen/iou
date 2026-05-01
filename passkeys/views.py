import datetime as dt
import json
import uuid
from typing import Protocol

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from webauthn import (
    base64url_to_bytes,
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import (
    bytes_to_base64url,
    options_to_json_dict,
    parse_authentication_credential_json,
)

from passkeys.models import Credential
from passkeys.service import get_user_credentials

User = get_user_model()

SESSION_KEY_CHALLENGE = "challenge"
WEBAUTHN_RP_NAME = "IOU"


@require_GET
@login_required
def index(request: HttpRequest):
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
        context={"options": options_dict, "credentials": get_user_credentials(user)},
        template_name="passkeys/index.html",
    )


class VerifiedRegistration(Protocol):
    credential_id: bytes
    credential_public_key: bytes


@require_POST
@login_required
def register_finish(request: HttpRequest):
    registration_verification: VerifiedRegistration = verify_registration_response(
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
    return redirect(reverse("passkeys:index"))


@require_GET
def login_start(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect(reverse("iou:index"))
    # https://github.com/duo-labs/py_webauthn/blob/master/examples/authentication.py
    authentication_options = generate_authentication_options(
        rp_id=request.get_host().split(":")[0],
    )
    options_dict = options_to_json_dict(authentication_options)
    request.session[SESSION_KEY_CHALLENGE] = options_dict["challenge"]

    return render(
        request,
        context={
            "options": options_dict,
        },
        template_name="passkeys/login_start.html",
    )


class AuthenticatorAssertionResponse(Protocol):
    user_handle: bytes


class AuthenticationCredential(Protocol):
    id: str
    response: AuthenticatorAssertionResponse


class VerifiedAuthentication(Protocol):
    user_verified: bool
    new_sign_count: int


@require_POST
def login_finish(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect(reverse("iou:index"))
    credential_json = json.loads(request.POST["credential_json"])
    request_credential: AuthenticationCredential = parse_authentication_credential_json(
        credential_json
    )
    db_credential = Credential.objects.filter(
        credential_id=request_credential.id
    ).first()
    if not db_credential:
        raise BadRequest()
    authentication_verification = verify_authentication_response(
        credential=credential_json,
        expected_challenge=base64url_to_bytes(
            request.session.get(SESSION_KEY_CHALLENGE)
        ),
        expected_origin=request.build_absolute_uri("/").rstrip("/"),
        expected_rp_id=request.get_host().split(":")[0],
        credential_current_sign_count=db_credential.sign_count,
        require_user_verification=True,
        credential_public_key=base64url_to_bytes(db_credential.public_key),
    )

    if not authentication_verification.user_verified:
        raise BadRequest()

    # No user handle, we can't verify that this is for the correct user:
    if not request_credential.response.user_handle:
        raise BadRequest()

    actual_user_uuid = uuid.UUID(bytes=request_credential.response.user_handle)
    expected_user_uuid = db_credential.user.uuid
    if actual_user_uuid != expected_user_uuid:
        raise BadRequest()

    db_credential.sign_count = authentication_verification.new_sign_count
    db_credential.last_used_at = dt.datetime.now(tz=dt.timezone.utc)
    db_credential.save()

    login(request, db_credential.user)

    return redirect(to=reverse("iou:index"))
