from decimal import Decimal
from itertools import chain

import re
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Model
from django.template.loader import get_template
from django_measurement.models import MeasurementField
from measurement.measures import Mass, Volume, Energy, Time
from django.utils.translation import gettext_lazy as _

# Create your models here.
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from nbconvert.filters import html2text
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, FieldRowPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel


def short(val):
    if len(val) > 34:
        return f"{val[:30]} ..."
    return val


def orders_in_cart(self: User):
    return sum(o.ordered_recipes.count() for o in self.orders.filter(status=OrderStatus.IN_CART).all())


User.add_to_class("orders_in_cart", orders_in_cart)


class ShopPreferences(Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shop_preferences")
    allow_reminders = models.BooleanField(verbose_name="Sta herinnerings mails toe", default=True, blank=False, null=False)
    last_reminder = models.DateTimeField(verbose_name="Laatste keer dat er een herinnering werd gestuurd", blank=True, null=True)
    show_vat = models.BooleanField(default=True)


class MeasurementHolder(object):
    VOLUME = [("ml", "ml"), ("dl", "dl"), ("l", "l"), ("us_tbsp", "eetlepel")]
    MASS = [("g", "g"), ("kg", "kg")]

    def get_measurement(self):
        for m in ["amount_mass", "amount_volume", "amount_units"]:
            if hasattr(self, m):
                return getattr(self, m)


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
    energy_per_kg = MeasurementField(measurement=Energy, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.scientific_name})"


class Ingredient(ClusterableModel, Orderable):
    name = models.CharField(max_length=1024, blank=False)
    description = RichTextField(blank=True, default="")
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    purchase_price = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    sell_price = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    price_unit = models.CharField(
        max_length=35, choices=[("g", "g"), ("kg", "kg"), ("l", "l"), ("ml", "ml"), (None, "")],
    blank=True)
    vat_pct = models.DecimalField(max_digits=5, decimal_places=2, default=6)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]

    @property
    def price_with_vat(self):
        return self.sell_price * (1 + self.vat_pct / 100)

    panels = [
        FieldRowPanel(
            [
                FieldPanel("name"),
                FieldPanel("purchase_price"),
                FieldPanel("sell_price"),
                FieldPanel("price_unit"),
                FieldPanel("vat_pct"),
                FieldPanel("is_available"),
            ]
        ),
        FieldPanel("description"),
        ImageChooserPanel("image"),
        InlinePanel("allergens", heading="Allergenen"),
        InlinePanel("nutrients", heading="Voedingsstoffen"),
    ]


class Recipe(ClusterableModel, Orderable):
    name = models.CharField(max_length=1024)
    description = RichTextField(blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )

    is_temporary = models.BooleanField(blank=False, default=False)
    purchase_price = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    sell_price = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    base_servings = models.IntegerField(default=1, validators=[MinValueValidator(Decimal("0.01"))])

    def __str__(self):
        return self.name

    @property
    def vat(self):
        return sum(i.vat for i in self.ingredients.all())

    @property
    def serving_price(self):
        return sum(i.price for i in self.ingredients.all())

    @property
    def serving_total_price(self):
        return sum(i.price for i in self.ingredients.all()) + self.serving_vat

    @property
    def serving_vat(self):
        return sum(i.vat for i in self.ingredients.all())

    @property
    def edit_allowed(self):
        return self.is_temporary and self.orders.count() <= 1

    @property
    def is_available(self):
        return all(i.ingredient.is_available for i in self.ingredients.all())

    def create_temp_copy(self, suffix_user="unknown", suffix_rand="0" * 6):
        old_ingredients = self.ingredients.all()
        new = Recipe.objects.get(id=self.id)
        new.id = None
        new.is_temporary = True
        if suffix_user in self.name:
            new.name = "-".join([*self.name.split("-")[:-1], suffix_rand])
        else:
            new.name = f"{self.name}-{suffix_user}-{suffix_rand}"
        new.save()
        for i in old_ingredients:
            r = RecipeIngredient(
                recipe=new,
                ingredient=i.ingredient,
                to_taste=i.to_taste,
                amount_mass=i.amount_mass,
                amount_units=i.amount_units,
                amount_volume=i.amount_volume,
                process_method=i.process_method,
                storage_method=i.storage_method,
            )
            r.save()
        new.save()
        return new

    def get_fix_repr(self):
        return "\n".join((f"€ {i.price_with_vat:.2f}: {i}" for i in self.ingredients.all()))

    panels = [
        FieldRowPanel([FieldPanel("name"), FieldPanel("is_temporary"), FieldPanel("base_servings"),]),
        FieldRowPanel([FieldPanel("purchase_price"), FieldPanel("sell_price")]),
        FieldPanel("description"),
        ImageChooserPanel("image"),
        InlinePanel("ingredients", heading="Ingredienten"),
    ]


class OrderStatus(models.TextChoices):
    IN_CART = "IC", _("In Cart")
    ORDERED = "OR", _("Ordered")
    ACCEPTED = "AC", _("Accepted")
    IN_PRODUCTION = "PR", _("In production")
    CREATED = "CR", _("Created")
    PAID = "PA", _("Paid")
    DELIVERED = "DE", _("Delivered")


class Order(ClusterableModel, Orderable):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders")
    status = models.CharField(max_length=2, choices=OrderStatus.choices, default=OrderStatus.IN_CART)
    delivery_date = models.DateTimeField(null=True, blank=True)
    cancelled = models.BooleanField(default=False)

    notes = models.TextField(default="", blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} {self.status} {self.created_at}"

    @property
    def show_vat(self):
        try:
            return self.user.shop_preferences.show_vat
        except:
            return True

    @property
    def total_price(self):
        return sum(
            chain(
                (o.total_price for o in self.ordered_recipes.all()),
                (o.user_total for o in self.custom_lines.all()),
            )
        )

    @property
    def total_vat(self):
        return sum(
            chain(
                (o.total_vat for o in self.ordered_recipes.all()),
                (l.total_vat for l in self.custom_lines.all()),
            )
        )

    @property
    def total_price_no_vat(self):
        return self.total_price - self.total_vat

    def advance_stage(self):
        if self.status == OrderStatus.IN_CART:
            self.status = OrderStatus.ORDERED
            for recipe in self.ordered_recipes.all():
                recipe.fixate_recipe()
            self.save()
            if self.user.email:
                self.mail_confirmation()
            return

    @property
    def is_available(self):
        return all(r.recipe.is_available for r in self.ordered_recipes.all())

    @classmethod
    def get_cart(cls: "Order", user: User):
        cart = cls.objects.filter(user=user, status=OrderStatus.IN_CART).first()
        if not cart:
            cart = Order(user=user)
            cart.save()
        return cart

    panels = [
        FieldRowPanel(
            [
                FieldPanel("user"),
                FieldPanel("status"),
                FieldPanel("delivery_date"),
                FieldPanel("cancelled"),
            ]
        ),
        FieldPanel("notes"),
        InlinePanel("ordered_recipes", heading="Bestelde Recepten"),
        InlinePanel("custom_lines", heading="Andere lijnen"),
    ]

    def mail_confirmation(self):
        if not self.delivery_date:
            return
        subj = f"Orderbevestiging Immuunthai #{self.id} ({self.delivery_date:%Y-%m-%d})"
        body = get_template("shop/email/order_confirmation.html")
        html_body = body.render({"self": self})
        self.user.email_user(subject=subj, message=html2text(html_body), html_message=html_body)


class ProcessMethod(Orderable):
    name = models.CharField(max_length=1024)
    description = RichTextField(blank=True)
    labour_multiplier = models.DecimalField(
        default=1, decimal_places=4, max_digits=5, validators=[MinValueValidator(Decimal("0.01"))]
    )

    def __str__(self):
        return f"{self.name}"


class StorageMethod(Orderable):
    name = models.CharField(max_length=1024)
    description = RichTextField(blank=True, default="")
    labour_multiplier = models.DecimalField(
        default=1, decimal_places=4, max_digits=5, validators=[MinValueValidator(Decimal("0.01"))]
    )
    conserves_for = MeasurementField(measurement=Time, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class IngredientAllergen(Orderable, MeasurementHolder):
    ingredient = ParentalKey(Ingredient, on_delete=models.CASCADE, related_name="allergens")
    allergen = models.ForeignKey(Allergen, on_delete=models.PROTECT)

    is_dangerous = models.BooleanField(default=False)
    is_trace_amount = models.BooleanField(default=False)
    amount_mass = MeasurementField(
        measurement=Mass, blank=True, null=True, validators=[MinValueValidator(0)]
    )
    amount_volume = MeasurementField(
        measurement=Volume, blank=True, null=True, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.ingredient} - {self.allergen} - {self.get_measurement()})"


class IngredientNutrition(Orderable, MeasurementHolder):
    ingredient = ParentalKey(Ingredient, on_delete=models.CASCADE, related_name="nutrients")
    nutrition = models.ForeignKey(Nutrition, on_delete=models.PROTECT)

    is_trace_amount = models.BooleanField(default=False)
    amount_mass = MeasurementField(
        measurement=Mass,
        blank=True,
        null=True,
        unit_choices=MeasurementHolder.MASS,
        verbose_name="Massa",
        validators=[MinValueValidator(0)],
    )
    amount_volume = MeasurementField(
        measurement=Volume,
        blank=True,
        null=True,
        unit_choices=MeasurementHolder.VOLUME,
        verbose_name="Volume",
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"{self.ingredient} - {self.nutrition} - {self.get_measurement()})"


class RecipeIngredient(Orderable, MeasurementHolder):
    recipe = ParentalKey(Recipe, on_delete=models.CASCADE, related_name="ingredients",)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

    to_taste = models.BooleanField(default=False, blank=True, null=True)

    amount_mass = MeasurementField(
        measurement=Mass,
        blank=True,
        null=True,
        unit_choices=MeasurementHolder.MASS,
        verbose_name="Massa",
        #validators=[MinValueValidator(Mass(g=0))],
    )
    amount_volume = MeasurementField(
        measurement=Volume,
        blank=True,
        null=True,
        unit_choices=MeasurementHolder.VOLUME,
        verbose_name="Volume",
        #validators=[MinValueValidator(Volume(ml=0))],
    )
    amount_units = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Aantal",
        validators=[MinValueValidator(0)],
    )

    process_method = models.ForeignKey(
        ProcessMethod, on_delete=models.PROTECT, blank=True, null=True
    )
    storage_method = models.ForeignKey(
        StorageMethod, on_delete=models.PROTECT, blank=True, null=True
    )

    def __str__(self):
        objs = [
            self.ingredient,
            self.get_measurement(),
            self.process_method,
            self.storage_method,
        ]
        return " - ".join(str(o) for o in objs if o)

    @property
    def price(self):
        return self.amount * self.ingredient.sell_price * self.price_multiplier

    @property
    def price_with_vat(self):
        return self.price * (1 + self.ingredient.vat_pct / 100)

    @property
    def vat(self):
        return self.price * self.ingredient.vat_pct / 100

    @property
    def amount(self):
        if self.amount_units:
            return Decimal(self.amount_units)
        units = self.amount_mass or self.amount_volume

        try:
            return Decimal(getattr(units, self.ingredient.price_unit)) or 1
        except AttributeError:
            return 0

    @property
    def unit(self):
        if self.amount_units:
            return "stuks"
        units = self.amount_mass or self.amount_volume
        return units.STANDARD_UNIT

    @property
    def price_multiplier(self):
        mult = 1
        if self.process_method:
            mult += self.process_method.labour_multiplier - 1
        if self.storage_method:
            mult += self.storage_method.labour_multiplier - 1
        return mult


class OrderRecipe(Orderable):
    order = ParentalKey(Order, on_delete=models.CASCADE, related_name="ordered_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, related_name="orders")

    amount_multiplier = models.DecimalField(
        default=1,
        decimal_places=2,
        max_digits=10,
        verbose_name="Aantal",
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    fixed_recipe = models.TextField(null=True, blank=True)
    sell_price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    sell_vat = models.DecimalField(
        max_digits=9,
        decimal_places=4,
        default=0,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    def __str__(self):
        return f"{self.recipe}\n{self.servings}\n{self.amount_multiplier} x € {self.recipe.serving_total_price:.2f} = € {self.total_price:.2f}"

    def fixate_recipe(self):
        self.sell_price = self.total_price
        self.sell_vat = self.total_vat
        self.fixed_recipe = f"{self}\n\n{self.recipe.get_fix_repr()}\n----------------------\n€ {self.recipe.serving_total_price:.2f}"
        self.save()

    @property
    def servings(self):
        return (
            f"{self.recipe.base_servings} x {self.amount_multiplier} = "
            f"{self.recipe.base_servings * self.amount_multiplier}"
        )

    @property
    def serving_price(self):
        return sum(i.price for i in self.recipe.ingredients.all()) + self.serving_vat

    @property
    def total_price(self):
        if self.sell_price:
            return self.sell_price
        return self.serving_price * self.amount_multiplier

    @property
    def serving_vat(self):
        if self.order.show_vat:
            return self.recipe.serving_vat
        return 0

    @property
    def total_vat(self):
        if self.sell_vat:
            return self.sell_vat
        return self.serving_vat * self.amount_multiplier


class OrderCustomLine(Orderable):
    order = ParentalKey(Order, on_delete=models.CASCADE, related_name="custom_lines")
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    vat_pct = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    description = models.TextField(default="")

    def __str__(self):
        return f"{self.order} - {self.quantity} x {self.unit_price} " f"{short(self.description)})"

    @property
    def user_price(self):
        if self.order.show_vat:
            return self.unit_price * (1 + self.vat_pct / 100)
        return self.unit_price

    @property
    def user_total(self):
        if self.order.show_vat:
            return self.unit_price * (1 + self.vat_pct / 100) * self.quantity
        return self.unit_price * self.quantity

    @property
    def total_vat(self):
        if self.order.show_vat:
            return self.unit_price * self.vat_pct / 100
        return 0
