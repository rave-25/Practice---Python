# Generated by Django 4.1.2 on 2022-10-14 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='totalhours',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]