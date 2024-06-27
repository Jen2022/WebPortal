from django.db import migrations, models


def add_initial_sports(apps, schema_editor):
    Sport = apps.get_model('backend', 'Sport')
    sports = [
        'gaelic football',
        'hurling',
        'camogie',
        'rugby',
        'soccer',
        'hockey',
        'basketball',
    ]
    for sport in sports:
        Sport.objects.create(name=sport, global_sport=True)


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),  # Ensure this matches your initial migration
    ]

    operations = [
        migrations.AddField(
            model_name='sport',
            name='global_sport',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sport',
            name='workspace',
            field=models.ForeignKey(
                'backend.Workspace', on_delete=models.CASCADE, related_name='sports', null=True, blank=True),
        ),
        migrations.RunPython(add_initial_sports),
    ]
