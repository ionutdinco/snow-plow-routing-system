# Generated by Django 4.0.3 on 2022-05-31 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snowplowrouting', '0015_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='schedule',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='snowplowrouting.schedule'),
        ),
    ]