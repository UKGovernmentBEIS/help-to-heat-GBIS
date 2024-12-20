# Generated by Django 3.2.19 on 2024-10-30 11:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0015_remove_length_limit_from_some_scottishepc_text_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scottishepcrating",
            name="co2_emissions",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="scottishepcrating",
            name="co2_emissions_per_floor_area",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="scottishepcrating",
            name="co2_emissions_potential",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="scottishepcrating",
            name="energy_consumption",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="scottishepcrating",
            name="floor_area",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="scottishepcrating",
            name="floor_height",
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="scottishepcrating",
            name="potential_energy_consumption",
            field=models.CharField(max_length=16, null=True),
        ),
    ]
