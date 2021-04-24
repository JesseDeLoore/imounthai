# -*- coding: utf-8 -*-
import factory
from django.conf import settings
from factory.django import DjangoModelFactory
from measurement.measures import Mass

from shop.models import Recipe, Order, Ingredient, RecipeIngredient, OrderRecipe, \
    ProcessMethod, StorageMethod


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('username',)

    username = factory.Faker("ascii_free_email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("ascii_free_email")
    is_staff = False
    is_active = True


class IngredientFactory(DjangoModelFactory):
    class Meta:
        model = Ingredient
        django_get_or_create = ('name',)

    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=25)
    image = None
    purchase_price = factory.Faker("pydecimal", min_value=1, max_value=3)
    sell_price = factory.Faker("pydecimal", min_value=4, max_value=8)
    price_unit = "kg"


class RecipeIngredientFactory(DjangoModelFactory):
    class Meta:
        model = RecipeIngredient
        django_get_or_create = ("recipe", "ingredient")


class RecipeFactory(DjangoModelFactory):
    class Meta:
        model = Recipe
        django_get_or_create = ('name',)

    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=25)
    image = None
    is_temporary = False
    purchase_price = factory.Faker("pydecimal", min_value=10, max_value=15)
    sell_price = factory.Faker("pydecimal", min_value=16, max_value=25)

    base_servings = 4

    @factory.post_generation
    def add_ingredients(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for ingredient, amount, unit in extracted:
            ingr_inst = IngredientFactory(name=ingredient)
            RecipeIngredientFactory(recipe=self, ingredient=ingr_inst, to_taste=False,
                                    amount_mass=Mass(**{unit: amount}))


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.RelatedFactory(UserFactory)
    notes = factory.Faker("sentence", nb_words=25)


class OrderRecipeFactory(DjangoModelFactory):
    class Meta:
        model = OrderRecipe
        django_get_or_create = ('order', 'recipe')

    amount_multiplier = 1


class ProcessMethodFactory(DjangoModelFactory):
    class Meta:
        model = ProcessMethod
        django_get_or_create = ("name",)

    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=25)
    labour_multiplier = 1

    @factory.post_generation
    def add_to_recipe_ingredients(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for ingredient, recipe in extracted:
            ingr_inst = IngredientFactory(name=ingredient)
            recipe_inst = RecipeFactory(name=recipe)
            i = RecipeIngredientFactory(recipe=recipe_inst, ingredient=ingr_inst)
            i.process_method = self
            i.save()


class StorageMethodFactory(DjangoModelFactory):
    class Meta:
        model = StorageMethod
        django_get_or_create = ("name",)

    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=25)
    labour_multiplier = 1

    @factory.post_generation
    def add_to_recipe_ingredients(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for ingredient, recipe in extracted:
            ingr_inst = IngredientFactory(name=ingredient)
            recipe_inst = RecipeFactory(name=recipe)
            i = RecipeIngredientFactory(recipe=recipe_inst, ingredient=ingr_inst)
            i.storage_method = self
            i.save()


