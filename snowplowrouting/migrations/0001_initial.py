# Generated by Django 4.0.3 on 2022-03-30 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=300)),
                ('token', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
