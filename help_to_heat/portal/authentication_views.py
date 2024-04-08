import logging

import segno
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from help_to_heat.portal import email_handler, models
from help_to_heat.utils import MethodDispatcher

logger = logging.getLogger(__name__)


def _strip_microseconds(dt):
    if not dt:
        return None
    return dt.replace(microsecond=0, tzinfo=None)


class LoginTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        email = user.email or ""
        token_timestamp = _strip_microseconds(user.last_login)
        return f"{user.pk}{user.password}{timestamp}{email}{token_timestamp}"


@require_http_methods(["GET", "POST"])
class CustomLoginView(MethodDispatcher):
    template_name = "account/login.html"
    credentials_error_message = (
        "Login failed - please check your credentials. If you believe they are correct, "
        "contact your team leader or our support team at "
        "eligibilitycheckersupport-cai@energysecurity.gov.uk"
    )
    invite_link_error_message = (
        "Login failed - please accept the invitation you were sent via email. If you have "
        "not received this, contact your team leader or our support team at "
        "eligibilitycheckersupport-cai@energysecurity.gov.uk"
    )

    def error(self, request, message):
        messages.error(request, message)
        return render(request, self.template_name)

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get("password", None)
        email = request.POST.get("login", None)
        if not password or not email:
            return self.error(request, "Please enter an email and password.")
        else:
            email = email.lower()
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.invite_accepted_at:
                    return self.error(request, self.invite_link_error_message)
                token = LoginTokenGenerator().make_token(user)
                return redirect("portal:verify-otp", user_id=user.id, token=token)
            else:
                return self.error(request, self.credentials_error_message)


@require_http_methods(["GET", "POST"])
class VerifyOTPView(MethodDispatcher):
    error_message = "Something has gone wrong.  Please contact your team leader."
    template_name = "account/verify-otp.html"

    def error(self, request):
        messages.error(request, self.error_message)
        return render(request, self.template_name)

    def get(self, request, user_id, token):
        return render(request, self.template_name)

    def post(self, request, user_id, token):
        otp = request.POST.get("otp", None)

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return self.error(request)

        token_valid = LoginTokenGenerator().check_token(user, token)
        if not token_valid:
            return self.error(request)

        if not otp:
            return self.error(request, message="Please enter the otp.")

        if not user.verify_otp(otp):
            return self.error(request)

        login(request, user)

        return redirect("portal:homepage")


@require_http_methods(["GET", "POST"])
class AcceptInviteView(MethodDispatcher):
    template_name = "account/accept_invite.html"
    error_message = "Something has gone wrong.  Please contact your team leader."

    def get(self, request):
        return render(request, self.template_name)

    def error(self, request):
        messages.error(request, self.error_message)
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", None)
        user_id = request.GET.get("user_id", "")
        token = request.GET.get("code", "")

        if not email:
            messages.error(request, "Please enter an email.")
            return render(request, self.template_name)

        try:
            user = models.User.objects.get(id=user_id, email=email)
        except models.User.DoesNotExist:
            return self.error(request)

        if user.invite_accepted_at:
            return self.error(request)

        if not user_id or not token:
            return self.error(request)

        result = email_handler.verify_token(user_id, token, "invite-user")
        if not result:
            return self.error(request)

        set_password_token = LoginTokenGenerator().make_token(user)

        return redirect("portal:account_login_set_password", user.id, set_password_token)


@require_http_methods(["GET", "POST"])
class SetPassword(MethodDispatcher):
    template_name = "account/login_set_password.html"
    error_message = "Something has gone wrong.  Please contact your team leader."

    def error(self, request, message=error_message):
        messages.error(request, message)
        return render(request, self.template_name)

    def get(self, request, user_id, token):
        return render(request, self.template_name, {"user_id": user_id})

    def post(self, request, user_id, token):
        user = models.User.objects.get(pk=user_id)

        token_valid = LoginTokenGenerator().check_token(user, token)
        if not token_valid:
            return self.error(request)

        pwd1 = request.POST.get("password1", None)
        pwd2 = request.POST.get("password2", None)
        if pwd1 != pwd2:
            return self.error(request, message="Passwords must match.")

        try:
            validate_password(pwd1)
        except ValidationError as e:
            for msg in e:
                messages.error(request, str(msg))
            return self.error(request, message="Please fix the errors and try again")

        user.set_password(pwd1)
        user.invite_accepted_at = timezone.now()
        user.save()
        messages.info(request, "Password successfully set.")

        mfa_setup_token = LoginTokenGenerator().make_token(user)

        return redirect("portal:mfa-setup", user_id=user_id, token=mfa_setup_token)


@require_http_methods(["GET", "POST"])
class MFASetup(MethodDispatcher):
    template_name = "account/mfa-setup.html"
    error_message = "Something has gone wrong. Please contact your team leader."

    def error(self, request, message=error_message):
        messages.error(request, message)
        return render(request, self.template_name)

    def get(self, request, user_id, token):
        user = models.User.objects.get(pk=user_id)
        totp_secret = user.get_totp_secret()
        uri = user.get_totp_uri()
        qr_code = segno.make(uri).svg_inline(scale=8)
        context = {
            "qr_code": qr_code,
            "totp_secret": totp_secret,
        }
        return render(request, self.template_name, context)

    def post(self, request, user_id, token):
        user = models.User.objects.get(pk=user_id)

        token_valid = LoginTokenGenerator().check_token(user, token)
        if not token_valid:
            return self.error(request)

        otp = request.POST.get("otp", None)
        secret = request.POST.get("totp_secret", None)

        if not otp:
            return self.error(request, message="Please enter the otp.")

        user_secret = user.get_totp_secret()

        if secret != user_secret:
            logger.error("Secret doesn't match")
            return self.error(request)

        if not user.verify_otp(otp):
            logger.error("Incorrect OTP")
            return self.error(request)

        login(request, user)

        return redirect("portal:homepage")


@require_http_methods(["GET", "POST"])
class PasswordReset(MethodDispatcher):
    def get(self, request):
        return render(request, "account/password_reset.html", {})

    def post(self, request):
        email = request.POST.get("email")
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            return redirect("portal:password-reset-done")
        email_handler.send_password_reset_email(user)
        return redirect("portal:password-reset-done")


@require_http_methods(["GET"])
def password_reset_done(request):
    return render(request, "account/password_reset_done.html", {})


@require_http_methods(["GET"])
def password_reset_from_key_done(request):
    return render(request, "account/password_reset_from_key_done.html", {})


@require_http_methods(["GET", "POST"])
class PasswordChange(MethodDispatcher):
    template_name = "account/password_reset_from_key.html"
    password_reset_error_message = (
        "This link is not valid. It may have expired or have already been used. Please try again."
    )

    def get_token_request_args(self, request):
        user_id = request.GET.get("user_id", None)
        token = request.GET.get("code", None)
        valid_request = False
        if not user_id or not token:
            logger.error("No user_id or no token")
            messages.error(request, self.password_reset_error_message)
        else:
            result = email_handler.verify_token(user_id, token, "password-reset")
            if not result:
                logger.error("No result")
                messages.error(request, self.password_reset_error_message)
            else:
                valid_request = True
        return user_id, token, valid_request

    def get(self, request):
        try:
            _, _, valid_request = self.get_token_request_args(request)
            return render(request, self.template_name, {"valid": valid_request})
        except models.User.DoesNotExist:
            return render(request, self.template_name, {"valid": False})

    def post(self, request):
        user_id, token, valid_request = self.get_token_request_args(request)
        pwd1 = request.POST.get("password1", None)
        pwd2 = request.POST.get("password2", None)
        if pwd1 != pwd2:
            logger.error("Passwords don't match")
            messages.error(request, "Passwords must match.")
            return render(request, self.template_name, {"valid": valid_request})
        if not valid_request:
            logger.error("Not valid request")
            messages.error(request, self.password_reset_error_message)
            return render(request, self.template_name, {"valid": valid_request})
        user = models.User.objects.get(pk=user_id)
        try:
            validate_password(pwd1, user)
        except ValidationError as e:
            for msg in e:
                logger.error(str(msg))
                messages.error(request, str(msg))
            return render(request, self.template_name, {"valid": valid_request})
        user.set_password(pwd1)
        user.save()

        mfa_setup_token = LoginTokenGenerator().make_token(user)

        return redirect("portal:mfa-setup", user_id=user_id, token=mfa_setup_token)
