import logging
import string

import pyotp
from dateutil import tz
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django_use_email_as_username.models import BaseUser, BaseUserManager

from help_to_heat import utils

epc_rating_choices = tuple((letter, letter) for letter in string.ascii_letters.upper()[:8])

logger = logging.getLogger(__name__)

london_tz = tz.gettz("Europe/London")


class SupplierChoices(utils.Choices):
    BRITISH_GAS = ("british-gas", "British Gas")
    BULB = ("bulb", "Bulb, now part of Octopus Energy")
    E_ENERGY = ("e-energy", "E (Gas & Electricity) Ltd")
    ECOTRICITY = ("ecotricity", "Ecotricity")
    EDF = ("edf", "EDF")
    EON = ("eon", "E.ON Next")
    FOXGLOVE = ("foxglove", "Foxglove")
    OCTOPUS = ("octopus", "Octopus Energy")
    OVO = ("ovo", "OVO")
    SCOTTISH_POWER = ("scottish-power", "Scottish Power")
    SHELL = ("shell", "Shell")
    SO_ENERGY = ("so-energy", "So Energy")
    UTILITA = ("utilita", "Utilita")
    UTILITY_WAREHOUSE = ("utility-warehouse", "Utility Warehouse")


class Supplier(utils.UUIDPrimaryKeyBase, utils.TimeStampedModel):
    name = models.CharField(max_length=256, unique=True)
    is_disabled = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f"<Supplier {self.name}>"

    def get_team_leader_count(self):
        return self.user_set.filter(role="TEAM_LEADER").count()


class UserRoleChoices(utils.Choices):
    SERVICE_MANAGER = "Service Manager"
    TEAM_LEADER = "Team Leader"
    TEAM_MEMBER = "Team Member"


class User(BaseUser, utils.UUIDPrimaryKeyBase):
    objects = BaseUserManager()
    username = None
    full_name = models.CharField(max_length=255, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, blank=True, null=True, on_delete=models.PROTECT)
    role = models.CharField(max_length=64, blank=True, null=True, choices=UserRoleChoices.choices)
    last_token_sent_at = models.DateTimeField(editable=False, blank=True, null=True)
    invited_at = models.DateTimeField(default=None, blank=True, null=True)
    invite_accepted_at = models.DateTimeField(default=None, blank=True, null=True)
    totp_key = models.CharField(max_length=255, blank=True, null=True)
    last_otp = models.CharField(max_length=8, blank=True, null=True)

    @property
    def referral_count(self):
        return self.supplier.referrals.count()

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        return super().save(*args, **kwargs)

    def get_totp_uri(self):
        secret = self.get_totp_secret()
        uri = pyotp.utils.build_uri(
            secret=secret,
            name=self.email,
            issuer=settings.TOTP_ISSUER,
        )
        return uri

    def get_totp_secret(self):
        if not self.totp_key:
            self.totp_key = utils.make_totp_key()
            self.save()
        totp_secret = utils.make_totp_secret(self.id, self.totp_key)
        return totp_secret

    def verify_otp(self, otp):
        if otp == self.last_otp:
            logger.error("OTP same as previous one")
            return False
        secret = self.get_totp_secret()
        totp = pyotp.TOTP(secret)
        success = totp.verify(otp)
        if success:
            self.last_otp = otp
            self.save()
        return success

    @property
    def is_service_manager(self):
        return self.role == "SERVICE_MANAGER"

    @property
    def is_team_leader(self):
        return self.role == "TEAM_LEADER"

    @property
    def is_team_member(self):
        return self.role == "TEAM_MEMBER"


class ReferralDownload(utils.UUIDPrimaryKeyBase, utils.TimeStampedModel):
    file_name = models.CharField(max_length=255, blank=True, null=True)
    last_downloaded_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)

    @property
    def local_created_at(self):
        return self.created_at.astimezone(london_tz)


class Referral(utils.UUIDPrimaryKeyBase, utils.TimeStampedModel):
    data = models.JSONField(encoder=DjangoJSONEncoder)
    supplier = models.ForeignKey(Supplier, blank=True, null=True, on_delete=models.PROTECT, related_name="referrals")
    session_id = models.UUIDField(editable=False, blank=True, null=True, unique=True)
    referral_download = models.ForeignKey(
        ReferralDownload,
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="referral_download",
    )
    referral_id = models.IntegerField(default=0)

    def __str__(self):
        return f"<referral id={self.id} supplier={self.supplier}>"

    def _do_insert(self, manager, using, fields, returning_fields, raw):
        # referral_id is SERIAL and so is auto generated
        # this will remove referral_id from the insert statement & so generate a new value
        ignore_fields = ["referral_id"]

        return super(Referral, self)._do_insert(
            manager, using, [field for field in fields if field.attname not in ignore_fields], returning_fields, raw
        )

    @property
    def formatted_referral_id(self):
        return f"GBIS{self.referral_id:07}"


class EpcRating(utils.TimeStampedModel):
    uprn = models.CharField(max_length=12, primary_key=True)
    rating = models.CharField(max_length=32, choices=epc_rating_choices)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"<EpcRating uprn={self.uprn}>"


class ScottishEpcRating(utils.TimeStampedModel):
    uprn = models.CharField(max_length=12, primary_key=True)
    rating = models.CharField(max_length=32, choices=epc_rating_choices)
    date = models.DateField(blank=True, null=True)
