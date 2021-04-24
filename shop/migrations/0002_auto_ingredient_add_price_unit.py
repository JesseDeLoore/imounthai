# Generated by Django 3.1.3 on 2021-04-18 17:22

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_squashed_0008_shoppreferences'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={},
        ),
        migrations.AddField(
            model_name='ingredient',
            name='price_unit',
            field=models.CharField(choices=[('g', 'g'), ('kg', 'kg'), ('l', 'l'), ('ml', 'ml'), (None, '')], max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='orderrecipe',
            name='order',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_recipes', to='shop.order'),
        ),
    ]