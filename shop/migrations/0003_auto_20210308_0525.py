# Generated by Django 3.1.3 on 2021-03-08 05:25

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20210307_1601'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={},
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='vat_pct',
        ),
        migrations.AlterField(
            model_name='ingredientallergen',
            name='ingredient',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='allergens', to='shop.ingredient'),
        ),
    ]