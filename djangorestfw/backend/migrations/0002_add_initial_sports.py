from django.db import migrations

def add_initial_sports(apps, schema_editor):
    Sport = apps.get_model('backend', 'Sport')
    sports = [
        {'name': 'gaelic football'},
        {'name': 'hurling'},
        {'name': 'camogie'},
        {'name': 'rugby'},
        {'name': 'soccer'},
        {'name': 'hockey'},
        {'name': 'basketball'},
    ]
    for sport in sports:
        Sport.objects.create(name=sport, global_sport=True)
    

class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0001_initial'),  # Ensure this matches your initial migration
    ]
    operations = [
        migrations.RunPython(add_initial_sports),
    ]