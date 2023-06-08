# Generated by Django 3.2.19 on 2023-06-08 19:14

import django.core.serializers.json
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('frontdoor', '0004_alter_answer_session_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('session_id', models.UUIDField(blank=True, editable=False, null=True)),
                ('data', models.JSONField(editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('page_name', models.CharField(editable=False, max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
