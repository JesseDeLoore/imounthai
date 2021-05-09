# Generated by Django 3.2.2 on 2021-05-09 08:48

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django_measurement.models
import measurement.base
import measurement.measures.mass
import measurement.measures.volume


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0008_auto_20210509_0744"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ingredientallergen",
            name="amount_mass",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.mass.Mass,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AlterField(
            model_name="ingredientallergen",
            name="amount_volume",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.volume.Volume,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AlterField(
            model_name="ingredientnutrition",
            name="amount_mass",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.mass.Mass,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Massa",
            ),
        ),
        migrations.AlterField(
            model_name="ingredientnutrition",
            name="amount_volume",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.volume.Volume,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Volume",
            ),
        ),
        migrations.AlterField(
            model_name="orderrecipe",
            name="amount_multiplier",
            field=models.DecimalField(
                decimal_places=2,
                default=1,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                verbose_name="Aantal",
            ),
        ),
        migrations.AlterField(
            model_name="orderrecipe",
            name="sell_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                default=0,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.AlterField(
            model_name="orderrecipe",
            name="sell_vat",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                default=0,
                max_digits=9,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.AlterField(
            model_name="processmethod",
            name="labour_multiplier",
            field=models.DecimalField(
                decimal_places=4,
                default=1,
                max_digits=5,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="base_servings",
            field=models.IntegerField(
                default=1, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))]
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="purchase_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                default=0,
                max_digits=7,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="sell_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=4,
                default=0,
                max_digits=7,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount_mass",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.mass.Mass,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Massa",
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount_units",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.base.MeasureBase,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Aantal",
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount_volume",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.volume.Volume,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Volume",
            ),
        ),
        migrations.AlterField(
            model_name="storagemethod",
            name="labour_multiplier",
            field=models.DecimalField(
                decimal_places=4,
                default=1,
                max_digits=5,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
    ]
