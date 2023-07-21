# Generated by Django 3.2.19 on 2023-07-21 14:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("frontdoor", "0007_answer_frontdoor_a_session_cfe892_idx"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="answer",
            name="frontdoor_a_session_cfe892_idx",
        ),
        migrations.AddIndex(
            model_name="answer",
            index=models.Index(
                fields=["session_id", "page_name", "-created_at"],
                include=("id", "data", "modified_at"),
                name="idx_answer_session_id",
            ),
        ),
    ]
