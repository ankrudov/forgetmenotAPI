# Generated by Django 4.2.3 on 2023-08-03 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_customuserv2_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuserv2',
            name='firebase_uid',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
