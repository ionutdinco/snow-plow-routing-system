# Generated by Django 4.0.3 on 2022-03-29 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_profile_status_profile_admin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='admin',
            new_name='is_admin',
        ),
    ]