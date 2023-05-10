# Generated by Django 4.2 on 2023-04-27 07:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecoplus", "0011_referraldownload"),
    ]

    operations = [
        migrations.AddField(
            model_name="referral",
            name="referral_download",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="referral_download",
                to="ecoplus.referraldownload",
            ),
        ),
    ]