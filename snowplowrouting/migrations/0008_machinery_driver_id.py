# Generated by Django 4.0.3 on 2022-04-03 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snowplowrouting', '0007_rename_employee_inviteemployee'),
    ]

    operations = [
        migrations.AddField(
            model_name='machinery',
            name='driver_id',
            field=models.IntegerField(null=True),
        ),
    ]
