# Generated by Django 4.0.3 on 2022-04-01 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snowplowrouting', '0002_addmachinery'),
    ]

    operations = [
        migrations.RenameField(
            model_name='addmachinery',
            old_name='series',
            new_name='vin',
        ),
    ]