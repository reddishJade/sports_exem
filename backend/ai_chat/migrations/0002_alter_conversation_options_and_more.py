# Generated by Django 5.1.7 on 2025-04-07 22:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_chat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversation',
            options={'ordering': ['-updated_at']},
        ),
        migrations.AddField(
            model_name='conversation',
            name='memory_summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='use_memory',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='title',
            field=models.CharField(default='新对话', max_length=255),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_conversations', to=settings.AUTH_USER_MODEL),
        ),
    ]
