from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

from help_to_heat.ecoplus import models, email_handler
from help_to_heat.ecoplus.utils import MethodDispatcher


@require_http_methods(["GET", "POST"])
class PasswordReset(MethodDispatcher):
    def get(self, request):
        return render(request, "account/password_reset.html", {})

    def post(self, request):
        email = request.POST.get("email")
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            return render(request, "account/password_reset_done.html", {})
        email_handler.send_password_reset_email(user)
        return render(request, "account/password_reset_done.html", {})
    

@require_http_methods(["GET", "POST"])
class PasswordChange(MethodDispatcher):
    password_reset_error_message = (
        "This link is not valid. It may have expired or have already been used. Please try again."
    )

    def get_token_request_args(self, request):
        user_id = request.GET.get("user_id", None)
        token = request.GET.get("code", None)
        valid_request = False
        if not user_id or not token:
            messages.error(request, self.password_reset_error_message)
        else:
            result = email_handler.verify_token(user_id, token, "password-reset")
            if not result:
                messages.error(request, self.password_reset_error_message)
            else:
                valid_request = True
        return user_id, token, valid_request

    def get(self, request):
        try:
            _, _, valid_request = self.get_token_request_args(request)
            return render(request, "account/password_reset_from_key.html", {"valid": valid_request})
        except models.User.DoesNotExist:
            return render(request, "account/password_reset_from_key.html", {"valid": False})

    def post(self, request):
        user_id, token, valid_request = self.get_token_request_args(request)
        pwd1 = request.POST.get("password1", None)
        pwd2 = request.POST.get("password2", None)
        one_time_password = request.POST.get("verification-code", None)
        if pwd1 != pwd2:
            messages.error(request, "Passwords must match.")
            return render(request, "account/password_reset_from_key.html", {"valid": valid_request})
        if not valid_request:
            messages.error(request, self.password_reset_error_message)
            return render(request, "account/password_reset_from_key.html", {"valid": valid_request})
        user = models.User.objects.get(pk=user_id)
        reset_requests = models.PasswordResetRequest.objects.filter(user=user, is_completed=False, is_abandoned=False)
        if not reset_requests:
            messages.error(request, self.password_reset_error_message)
            return render(request, "account/password_reset_from_key.html", {"valid": valid_request})
        token_matching_reset_request = None
        for reset_request in reset_requests:
            if check_password(one_time_password.lower(), reset_request.one_time_password):
                token_matching_reset_request = reset_request
                break
        if not token_matching_reset_request:
            messages.error(request, self.password_reset_error_message)
            return render(request, "account/password_reset_from_key.html", {"valid": valid_request})
        try:
            validate_password(pwd1, user)
        except ValidationError as e:
            for msg in e:
                messages.error(request, str(msg))
            return render(request, "account/password_reset_from_key.html", {"valid": valid_request})
        token_matching_reset_request.is_completed = True
        token_matching_reset_request.save()
        user.set_password(pwd1)
        user.save()
        return render(request, "account/password_reset_from_key_done.html", {})
