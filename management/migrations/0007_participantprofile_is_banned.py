# Generated by Django 5.1.7 on 2025-04-05 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_teamjoinrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='participantprofile',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
    ]
