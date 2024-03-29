# Generated by Django 3.2.5 on 2021-09-04 18:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_ingredient_ordering_dimless_units'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount_units',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Aantal'),
        ),
    ]
