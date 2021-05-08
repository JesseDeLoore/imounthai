# Generated by Django 3.1.3 on 2021-05-08 12:12
# Add verbose names to fields visible in the UI
# Add fixed_recipe logic to OrderRecipe to preserve pricing history

from django.db import migrations, models
import django.db.models.deletion
import django_measurement.models
import measurement.base
import measurement.measures.mass
import measurement.measures.volume


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0004_auto_20210424_0757"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderrecipe",
            name="fixed_recipe",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="ingredientnutrition",
            name="amount_mass",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.mass.Mass,
                null=True,
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
                verbose_name="Volume",
            ),
        ),
        migrations.AlterField(
            model_name="orderrecipe",
            name="amount_multiplier",
            field=models.DecimalField(
                decimal_places=2, default=1, max_digits=10, verbose_name="Aantal"
            ),
        ),
        migrations.AlterField(
            model_name="orderrecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="orders", to="shop.recipe"
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="purchase_price",
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="sell_price",
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount_mass",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.mass.Mass,
                null=True,
                verbose_name="Massa",
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount_units",
            field=django_measurement.models.MeasurementField(
                blank=True, measurement=measurement.base.MeasureBase, null=True, verbose_name="Aantal"
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount_volume",
            field=django_measurement.models.MeasurementField(
                blank=True,
                measurement=measurement.measures.volume.Volume,
                null=True,
                verbose_name="Volume",
            ),
        ),
    ]
