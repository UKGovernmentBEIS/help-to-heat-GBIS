from dateutil import tz
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from help_to_heat import utils

london_tz = tz.gettz("Europe/London")


class Event(utils.TimeStampedModel):
    name = models.CharField(max_length=256)
    data = models.JSONField(encoder=DjangoJSONEncoder)


class AccessToken(utils.TimeStampedModel):
    access_token = models.CharField(max_length=65535)


class Answer(utils.UUIDPrimaryKeyBase, utils.TimeStampedModel):
    data = models.JSONField(encoder=DjangoJSONEncoder, editable=False)
    page_name = models.CharField(max_length=128, editable=False)
    session_id = models.UUIDField(editable=False)

    class Meta:
        indexes = [models.Index(fields=["session_id"])]


class FeedbackDownload(utils.UUIDPrimaryKeyBase, utils.TimeStampedModel):
    file_name = models.CharField(max_length=255, blank=True, null=True)

    @property
    def local_created_at(self):
        return self.created_at.astimezone(london_tz)


class Feedback(utils.UUIDPrimaryKeyBase, utils.TimeStampedModel):
    session_id = models.UUIDField(editable=False, blank=True, null=True)
    page_name = models.CharField(max_length=128, editable=False, blank=True, null=True)
    data = models.JSONField(encoder=DjangoJSONEncoder, editable=False)
    feedback_download = models.ForeignKey(
        FeedbackDownload,
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="feedback_download",
    )

    def __str__(self):
        return f"<feedback id={self.id} page_name={self.page_name}>"
