# Generated by Django 2.2.5 on 2020-01-06 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0043_auto_20191213_0248'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='mode',
            field=models.CharField(blank=True, choices=[('quick_mode', 'Quick Mode'), ('contract_mode', 'Contract Mode')], max_length=14, null=True),
        ),
    ]
