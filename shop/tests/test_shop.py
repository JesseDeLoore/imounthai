# -*- coding: utf-8 -*-
import pytest

from shop.models import Ingredient, OrderRecipe
from shop.tests.conftest import set_prices
from shop.tests.factories.shop_factories import ProcessMethodFactory, \
    StorageMethodFactory


@pytest.mark.django_db
def test_recipe_creation(basic_recipe):
    assert basic_recipe.ingredients.count() == 3
    assert basic_recipe.name == "Fruitpap"


@pytest.mark.django_db
def test_recipe_price(basic_order: OrderRecipe):
    set_prices([("banaan", 2.5), ('kiwi', 3.5), ("appel", 4.5)])
    ingredients = basic_order.recipe.ingredients.all()
    assert ingredients[0].get_measurement().kg == 0.05
    assert ingredients[1].get_measurement().kg == 0.07
    assert ingredients[2].get_measurement().kg == 0.13
    assert ingredients[2].ingredient.vat_pct == 6
    assert ingredients[2].ingredient.sell_price == 4.5
    assert basic_order.order.total_price == basic_order.total_price
    assert basic_order.order.total_vat == basic_order.total_vat
    assert pytest.approx(basic_order.order.total_price_no_vat,
                         1e-4) == basic_order.total_price - basic_order.total_vat
    assert basic_order.amount_multiplier == 1
    assert basic_order.order.show_vat
    price = 1.06 * (2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    vat = 0.06 * (2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    assert pytest.approx(float(basic_order.total_price), 1e-6) == price
    assert pytest.approx(float(basic_order.total_vat), 1e-6) == vat


@pytest.mark.django_db
def test_recipe_price_with_multiplier(basic_order: OrderRecipe):
    set_prices([("banaan", 2.5), ('kiwi', 3.5), ("appel", 4.5)])
    p = ProcessMethodFactory(name="Schillen", labour_multiplier=1.3,
                             add_to_recipe_ingredients=[("banaan", "Fruitpap")])
    # vat * sum(ingredient_amount * price * multipliers)
    price = 1.06 * (1.3 * 2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    assert pytest.approx(float(basic_order.total_price), 1e-6) == price
    s = StorageMethodFactory(name="Vacuum", labour_multiplier=1.1,
                             add_to_recipe_ingredients=[("banaan", "Fruitpap"),
                                                        ("kiwi", "Fruitpap")])
    price = 1.06 * ((1 + 0.3 + 0.1) * 2.5 * 0.05 + 1.1 * 3.5 * 0.07 + 4.5 * 0.13)
    assert basic_order.order.total_price == basic_order.total_price
    assert basic_order.order.total_vat == basic_order.total_vat
    assert pytest.approx(basic_order.order.total_price_no_vat,
                         1e-6) == basic_order.total_price - basic_order.total_vat
    assert pytest.approx(float(basic_order.total_price),1e-6) == price
