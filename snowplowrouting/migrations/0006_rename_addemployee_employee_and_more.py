# Generated by Django 4.0.3 on 2022-04-03 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snowplowrouting', '0005_remove_addemployee_id_remove_addmachinery_id_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AddEmployee',
            new_name='Employee',
        ),
        migrations.RenameModel(
            old_name='AddMachinery',
            new_name='Machinery',
        ),
    ]
