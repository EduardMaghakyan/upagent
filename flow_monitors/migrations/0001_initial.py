# Generated by Django 5.1.7 on 2025-04-04 19:55

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowMonitor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('starting_url', models.URLField(help_text='Starting URL for the flow')),
                ('interval_seconds', models.IntegerField(default=3600, help_text='Check interval (hourly, daily, etc.)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flow_monitors', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FlowStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sequence', models.IntegerField(help_text='Order of execution')),
                ('action_type', models.CharField(choices=[('navigate', 'Navigate to URL'), ('click', 'Click Element'), ('fill', 'Fill Form Field'), ('wait', 'Wait for Element'), ('verify', 'Verify Element Exists')], max_length=20)),
                ('description', models.CharField(help_text='Human readable description', max_length=255)),
                ('url', models.URLField(blank=True, help_text='URL to navigate to', null=True)),
                ('element_description', models.CharField(blank=True, help_text='Text description of element to interact with', max_length=255, null=True)),
                ('input_value', models.CharField(blank=True, help_text='Value to input into form field', max_length=255, null=True)),
                ('timeout_seconds', models.IntegerField(default=30)),
                ('wait_time_seconds', models.IntegerField(default=0, help_text='Time to wait after action')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='flow_monitors.flowmonitor')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.CreateModel(
            name='FlowCheck',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_successful', models.BooleanField()),
                ('total_time', models.FloatField(help_text='Total flow execution time in seconds')),
                ('error_message', models.TextField(blank=True, null=True)),
                ('screenshot', models.ImageField(blank=True, null=True, upload_to='flow_screenshots/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('flow_monitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checks', to='flow_monitors.flowmonitor')),
                ('error_step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='failures', to='flow_monitors.flowstep')),
            ],
        ),
    ]
