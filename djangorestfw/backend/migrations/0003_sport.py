# Generated by Django 5.0.6 on 2024-06-19 16:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0002_teamcategory"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]
