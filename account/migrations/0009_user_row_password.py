# Generated by Django 3.2.9 on 2022-02-13 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20220206_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='row_password',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]