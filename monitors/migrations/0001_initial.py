# Generated by Django 5.1.7 on 2025-03-23 21:23

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('url', models.CharField(help_text='URL for HTTP or IP address for PING', max_length=255)),
                ('monitor_type', models.CharField(choices=[('http', 'HTTP'), ('ping', 'PING')], max_length=10)),
                ('interval_seconds', models.IntegerField(default=300, help_text='Check interval in seconds')),
                ('timeout_seconds', models.IntegerField(default=30, help_text='Timeout in seconds')),
                ('expected_status_code', models.IntegerField(blank=True, default=200, help_text='For HTTP monitors only', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Check',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_up', models.BooleanField()),
                ('response_time', models.FloatField(blank=True, help_text='Response time in milliseconds', null=True)),
                ('status_code', models.IntegerField(blank=True, help_text='HTTP status code (HTTP monitors only)', null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('monitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checks', to='monitors.monitor')),
            ],
        ),
    ]
