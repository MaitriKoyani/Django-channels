# Generated by Django 5.1.5 on 2025-01-22 11:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_rename_user_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='username',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_user_auth_token', to=settings.AUTH_USER_MODEL),
        ),
    ]
