# Generated by Django 2.2.5 on 2019-11-16 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0025_auto_20191115_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='accept_offer',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='yes', max_length=3),
            preserve_default=False,
        ),
    ]
