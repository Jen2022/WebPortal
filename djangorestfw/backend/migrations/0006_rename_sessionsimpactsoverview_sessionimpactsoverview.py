# Generated by Django 5.0.6 on 2024-07-02 10:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0005_rename_sessionimpacts_sessionimpact"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="SessionsImpactsOverview",
            new_name="SessionImpactsOverview",
        ),
    ]
