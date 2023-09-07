import logging

import furl
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from help_to_heat.portal import models

logger = logging.getLogger(__name__)


def _strip_microseconds(dt):
    if not dt:
        return None
    return dt.replace(microsecond=0, tzinfo=None)


class EmailVerifyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        email = user.email or ""
        token_timestamp = _strip_microseconds(user.last_token_sent_at)
        return f"{user.pk}{user.password}{timestamp}{email}{token_timestamp}"


class PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        login_timestamp = _strip_microseconds(user.last_login)
        email = user.email or ""
        token_timestamp = _strip_microseconds(user.last_token_sent_at)
        return f"{user.pk}{user.password}{login_timestamp}{timestamp}{email}{token_timestamp}"


class InviteTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        invited_timestamp = _strip_microseconds(user.invited_at)
        email = user.email or ""
        token_timestamp = _strip_microseconds(user.last_token_sent_at)
        return f"{user.pk}{invited_timestamp}{timestamp}{email}{token_timestamp}"


EMAIL_VERIFY_TOKEN_GENERATOR = EmailVerifyTokenGenerator()
PASSWORD_RESET_TOKEN_GENERATOR = PasswordResetTokenGenerator()
INVITE_TOKEN_GENERATOR = InviteTokenGenerator()


EMAIL_MAPPING = {
    "password-reset": {
        "from_address": settings.FROM_EMAIL,
        "subject": "Great British Insulation Scheme: password reset",
        "template_name": "portal/email/password-reset.txt",
        "url_name": "portal:password-reset-change",
        "token_generator": PASSWORD_RESET_TOKEN_GENERATOR,
    },
    "invite-user": {
        "from_address": settings.FROM_EMAIL,
        "subject": "Great British Insulation Scheme: invitation to system",
        "template_name": "portal/email/invite-user.txt",
        "url_name": "portal:accept-invite",
        "token_generator": INVITE_TOKEN_GENERATOR,
    },
    "referral-confirmation": {
        "from_address": settings.FROM_EMAIL,
        "template_name": "portal/email/referral-confirmation.txt",
    },
    "referral-confirmation-cy": {
        "from_address": settings.FROM_EMAIL,
        "template_name": "portal/email/referral-confirmation-cy.txt",
    },
}


def _send_token_email(user, subject, template_name, from_address, url_name, token_generator):
    user.last_token_sent_at = timezone.now()
    user.save()
    token = token_generator.make_token(user)
    base_url = settings.BASE_URL
    url_path = reverse(url_name)
    url = str(furl.furl(url=base_url, path=url_path, query_params={"code": token, "user_id": str(user.id)}))
    context = dict(user=user, url=url, contact_address=settings.CONTACT_EMAIL)
    body = render_to_string(template_name, context)
    try:
        response = send_mail(
            subject=subject,
            message=body,
            from_email=from_address,
            recipient_list=[user.email],
        )
        return response
    except Exception:  # noqa: B902
        logger.exception("An error occured while attempting to send an email.")


def _send_normal_email(subject, template_name, from_address, to_address, context):
    body = render_to_string(template_name, context)
    try:
        response = send_mail(
            subject=subject,
            message=body,
            from_email=from_address,
            recipient_list=[to_address],
        )
        return response
    except Exception:  # noqa: B902
        logger.exception("An error occured while attempting to send an email.")


def send_password_reset_email(user):
    data = EMAIL_MAPPING["password-reset"]
    return _send_token_email(user, **data)


def send_invite_email(user):
    data = EMAIL_MAPPING["invite-user"]
    user.invited_at = timezone.now()
    user.save()
    return _send_token_email(user, **data)


def send_referral_confirmation_email(session_data, language_code):
    if language_code.startswith("cy"):
        data = EMAIL_MAPPING["referral-confirmation-cy"]
        data["subject"] = "Cwblhau atgyfeiriad"
    else:
        data = EMAIL_MAPPING["referral-confirmation"]
        data["subject"] = f"Referral to {session_data.get('supplier')} successful"
    context = {"supplier_name": session_data.get("supplier")}
    return _send_normal_email(to_address=session_data.get("email"), context=context, **data)


def verify_token(user_id, token, token_type):
    user = models.User.objects.get(id=user_id)
    result = EMAIL_MAPPING[token_type]["token_generator"].check_token(user, token)
    return result
