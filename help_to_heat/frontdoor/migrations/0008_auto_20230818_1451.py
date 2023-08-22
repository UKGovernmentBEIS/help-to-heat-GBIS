# Generated by Django 3.2.19 on 2023-08-18 14:51

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("frontdoor", "0007_answer_frontdoor_a_session_cfe892_idx"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedbackDownload",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("file_name", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="feedback",
            name="feedback_download",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="feedback_download",
                to="frontdoor.feedbackdownload",
            ),
        ),
    ]