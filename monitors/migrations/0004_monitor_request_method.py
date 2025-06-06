# Generated by Django 5.1.7 on 2025-03-30 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0003_monitor_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor',
            name='request_method',
            field=models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE'), ('OPTIONS', 'OPTIONS'), ('HEAD', 'HEAD')], default='GET', help_text='HTTP request method (HTTP monitors only)', max_length=10),
        ),
    ]
