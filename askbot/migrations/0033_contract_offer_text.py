# Generated by Django 2.2.5 on 2019-11-22 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0032_auto_20191122_0454'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='offer_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
