# Generated by Django 4.0.3 on 2022-06-08 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snowplowrouting', '0019_driver_route'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('county', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('configArea', models.CharField(max_length=50)),
                ('startApp', models.BooleanField(default=False)),
            ],
        ),
    ]
