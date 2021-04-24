# -*- coding: utf-8 -*-
from typing import List, Tuple

import pytest

from shop.models import Ingredient
from shop.tests.factories.shop_factories import RecipeFactory, OrderFactory, \
    OrderRecipeFactory, UserFactory


@pytest.fixture
@pytest.mark.django_db
def basic_recipe():
    return RecipeFactory(
        name="Fruitpap",
        add_ingredients=[
            ("banaan", "50", "g"),
            ("kiwi", "0.070", "kg"),
            ("appel", "0.130", "kg"),
        ],
    )


def set_prices(ingredient_price_list: List[Tuple[str, float]]):
    for ingredient, price in ingredient_price_list:
        i = Ingredient.objects.get(name=ingredient)
        i.sell_price = price
        i.save()


@pytest.fixture
@pytest.mark.django_db
def basic_order(basic_recipe):
    user = UserFactory()
    order = OrderFactory(user_id=user.id)
    return OrderRecipeFactory(order=order, recipe=basic_recipe)
