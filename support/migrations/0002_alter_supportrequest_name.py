# Generated by Django 5.1.7 on 2025-03-30 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportrequest',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
