# Generated by Django 3.2.19 on 2023-07-18 15:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("frontdoor", "0006_remove_answer_unique answer per page per session"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="answer",
            index=models.Index(fields=["session_id"], name="frontdoor_a_session_cfe892_idx"),
        ),
    ]
