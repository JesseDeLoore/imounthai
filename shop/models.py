from django.contrib.auth.models import User
from django.db import models
from django_measurement.models import MeasurementField
from measurement.base import MeasureBase
from measurement.measures import Mass, Volume, Energy, Time
from django.utils.translation import gettext_lazy as _
# Create your models here.
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, FieldRowPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel


def short(val):
    if len(val) > 30:
        return f"{val[:30]} ..."
    return val


class MeasurementHolder(object):
    VOLUME = [("ml", "ml"), ("dl", "dl"), ("l", "l"), ("us_tbsp", "tablespoon")]
    MASS = [("g", "g"), ("kg", "kg")]

    def get_measurement(self):
        for m in ["amount_mass", "amount_volume", "amount_units"]:
            if hasattr(self, m):
                return getattr(self, m)


class ShopUser(User):
    show_vat = models.BooleanField(default=True)


class Allergen(Orderable):
    name = models.CharField(max_length=1024, blank=False)
    description = RichTextField(blank=True, default="")
    code = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({short(self.description)})"


class Nutrition(Orderable):
    name = models.CharField(max_length=1024, blank=False)
    scientific_name = models.CharField(max_length=1024, blank=True, default="")
    description = RichTextField(blank=True, null=True)
    energy_per_kg = MeasurementField(measurement=Energy, null=True)

    def __str__(self):
        return f"{self.name} ({self.scientific_name})"


class Ingredient(ClusterableModel, Orderable):
    name = models.CharField(max_length=1024, blank=False)
    description = RichTextField(blank=True, default="")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    purchase_price = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    sell_price = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    vat_pct = models.DecimalField(max_digits=5, decimal_places=2, default=6)

    def __str__(self):
        return f"{self.name} ({short(self.description)})"

    panels = [FieldRowPanel([
        FieldPanel('name'),
        FieldPanel('purchase_price'),
        FieldPanel('sell_price'),
        FieldPanel('vat_pct'),
    ]),
        FieldPanel('description'),
        ImageChooserPanel('image'),
        InlinePanel('allergens', heading="Allergenen"),
        InlinePanel('nutrients', heading="Voedingsstoffen"),
    ]


class Recipe(ClusterableModel, Orderable):
    name = models.CharField(max_length=1024)
    description = RichTextField(blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    is_temporary = models.BooleanField(blank=False, default=False)
    purchase_price = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    sell_price = models.DecimalField(max_digits=7, decimal_places=4, default=0)

    def __str__(self):
        return f"{self.name} [{self.sell_price}] ({short(self.description)})"

    @property
    def vat(self):
        return sum(self.ingredients.vat)

    base_servings = models.IntegerField(default=1)

    panels = [FieldRowPanel([
        FieldPanel('name'),
        FieldPanel('purchase_price'),
        FieldPanel('sell_price'),
        FieldPanel('is_temporary'),
    ]),
        FieldPanel('description'),
        ImageChooserPanel('image'),
        InlinePanel('ingredients', heading="Ingredienten"),
    ]


class OrderStatus(models.TextChoices):
    IN_CART = 'IC', _('In Cart')
    ORDERED = 'OR', _('Ordered')
    ACCEPTED = 'AC', _('Accepted')
    IN_PRODUCTION = 'PR', _('In production')
    CREATED = 'CR', _('Created')
    PAID = 'PA', _('Paid')
    DELIVERED = 'DE', _('Delivered')


class Order(ClusterableModel, Orderable):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=OrderStatus.choices, default=OrderStatus.IN_CART)
    delivery_date = models.DateTimeField()
    cancelled = models.BooleanField(default=False)

    notes = models.TextField(default="")

    def __str__(self):
        return f"{self.user.get_full_name()} {self.status} {self.created_at}"

    @property
    def total_price(self):
        return sum(self.orders.total_price) + sum(self.custom_lines.user_total)

    @property
    def total_vat(self):
        return sum(self.orders.total_vat) + sum(self.custom_lines.total_vat)

    @property
    def total_price_no_vat(self):
        return self.total_price - self.total_vat

    panels = [FieldRowPanel([
        FieldPanel('user'),
        FieldPanel('status'),
        FieldPanel('delivery_date'),
        FieldPanel('cancelled'),
    ]),
        FieldPanel('notes'),
        InlinePanel('orders', heading="Bestelde Recepten"),
        InlinePanel('custom_lines', heading="Andere lijnen"),
    ]

class ProcessMethod(Orderable):
    name = models.CharField(max_length=1024)
    description = RichTextField(blank=True)
    labour_multiplier = models.FloatField(default=1)

    def __str__(self):
        return f"{self.name} ({short(self.description)})"


class StorageMethod(Orderable):
    name = models.CharField(max_length=1024)
    description = RichTextField(blank=True, default="")
    labour_multiplier = models.FloatField(default=1)
    conserves_for = MeasurementField(measurement=Time, null=True)

    def __str__(self):
        return f"{self.name} ({short(self.description)})"


class IngredientAllergen(Orderable, MeasurementHolder):
    ingredient = ParentalKey(Ingredient, on_delete=models.CASCADE, related_name="allergens")
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE)

    is_dangerous = models.BooleanField(default=False)
    is_trace_amount = models.BooleanField(default=False)
    amount_mass = MeasurementField(measurement=Mass, null=True)
    amount_volume = MeasurementField(measurement=Volume, null=True)

    def __str__(self):
        return f"{self.ingredient} - {self.allergen} - {self.get_measurement()})"


class IngredientNutrition(Orderable, MeasurementHolder):
    ingredient = ParentalKey(Ingredient, on_delete=models.CASCADE, related_name="nutrients")
    nutrition = models.ForeignKey(Nutrition, on_delete=models.CASCADE)

    is_trace_amount = models.BooleanField(default=False)
    amount_mass = MeasurementField(measurement=Mass, null=True)
    amount_volume = MeasurementField(measurement=Volume, null=True,
                                     unit_choices=MeasurementHolder.VOLUME)

    def __str__(self):
        return f"{self.ingredient} - {self.nutrition} - {self.get_measurement()})"


class RecipeIngredient(Orderable, MeasurementHolder):
    recipe = ParentalKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    to_taste = models.BooleanField(default=False, null=True)

    amount_mass = MeasurementField(measurement=Mass, null=True)
    amount_volume = MeasurementField(measurement=Volume, null=True)
    amount_units = MeasurementField(measurement=MeasureBase, null=True)

    process_method = models.ForeignKey(ProcessMethod, on_delete=models.SET_NULL, null=True)
    storage_method = models.ForeignKey(StorageMethod, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.recipe} - {self.ingredient} - {self.get_measurement()})"

    @property
    def price(self):
        return self.amount * self.ingredient.sell_price

    @property
    def vat(self):
        return self.amount * self.ingredient.sell_price * self.ingredient.vat_pct

    @property
    def amount(self):
        return self.amount_mass or self.amount_volume or self.amount_units or 1


class OrderRecipe(Orderable):
    order = ParentalKey(Order, on_delete=models.CASCADE, related_name="orders")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    amount_multiplier = models.DecimalField(default=1, decimal_places=2, max_digits=10)


    def __str__(self):
        return f"{self.order} - {self.recipe} - {self.amount_multiplier})"

    @property
    def servings(self):
        return f"{self.recipe.base_servings} x {self.amount_multiplier} = " \
               f"{self.recipe.base_servings * self.amount_multiplier}"

    @property
    def total_price(self):
        if self.order.user.show_vat:
            return self.recipe.sell_price * (1 + self.recipe.vat_pct) * self.amount_multiplier
        return self.recipe.sell_price * self.amount_multiplier

    @property
    def total_vat(self):
        if self.order.user.show_vat:
            return self.recipe.vat * self.recipe.vat_pct * self.amount_multiplier
        return 0


class OrderCustomLine(Orderable):
    order = ParentalKey(Order, on_delete=models.CASCADE, related_name="custom_lines")
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)
    vat_pct = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    description = models.TextField(default="")


    def __str__(self):
        return f"{self.order} - {self.quantity} x {self.unit_price} {short(self.description)})"

    @property
    def user_price(self):
        if self.order.user.show_vat:
            return self.unit_price * (1 + self.vat_pct)
        return self.unit_price

    @property
    def user_total(self):
        if self.order.user.show_vat:
            return self.unit_price * (1 + self.vat_pct) * self.quantity
        return self.unit_price * self.quantity

    @property
    def total_vat(self):
        if self.order.user.show_vat:
            return self.unit_price * (self.vat_pct)
        return 0
