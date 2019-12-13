# Generated by Django 2.2.5 on 2019-12-13 02:38

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0041_remove_contract_offer_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='amount',
            field=models.DecimalField(decimal_places=8, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.0006'))]),
        ),
    ]
