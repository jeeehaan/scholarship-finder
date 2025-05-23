# Generated by Django 5.2.1 on 2025-05-19 15:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0003_rename_url_scholarship_official_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="scholarship",
            name="must_relocate",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scholarship",
            name="study_format",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="scholarship",
            name="country",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100), size=None
            ),
        ),
        migrations.AlterField(
            model_name="scholarship",
            name="official_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
