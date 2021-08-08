# -*- coding: utf-8 -*-
from datetime import datetime

import pytest
from django.test import Client

from shop.models import Ingredient, OrderRecipe, OrderStatus
from shop.tests.conftest import set_prices
from shop.tests.factories.shop_factories import (
    ProcessMethodFactory,
    StorageMethodFactory,
    OrderFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_recipe_creation(basic_recipe):
    assert basic_recipe.ingredients.count() == 3
    assert basic_recipe.name == "Fruitpap"


@pytest.mark.django_db
def test_recipe_price(basic_order: OrderRecipe):
    set_prices([("banaan", 2.5), ("kiwi", 3.5), ("appel", 4.5)])
    ingredients = basic_order.recipe.ingredients.all()
    assert ingredients[0].get_measurement().kg == 0.05
    assert ingredients[1].get_measurement().kg == 0.07
    assert ingredients[2].get_measurement().kg == 0.13
    assert ingredients[2].ingredient.vat_pct == 6
    assert ingredients[2].ingredient.sell_price == 4.5
    assert basic_order.order.total_price == basic_order.total_price
    assert basic_order.order.total_vat == basic_order.total_vat
    assert (
        pytest.approx(basic_order.order.total_price_no_vat, 1e-4)
        == basic_order.total_price - basic_order.total_vat
    )
    assert basic_order.amount_multiplier == 1
    assert basic_order.order.show_vat
    price = 1.06 * (2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    vat = 0.06 * (2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    assert pytest.approx(float(basic_order.total_price), 1e-6) == price
    assert pytest.approx(float(basic_order.total_vat), 1e-6) == vat


@pytest.mark.django_db
def test_recipe_price_with_multiplier(basic_order: OrderRecipe):
    set_prices([("banaan", 2.5), ("kiwi", 3.5), ("appel", 4.5)])
    p = ProcessMethodFactory(
        name="Schillen", labour_multiplier=1.3, add_to_recipe_ingredients=[("banaan", "Fruitpap")],
    )
    # vat * sum(ingredient_amount * price * multipliers)
    price = 1.06 * (1.3 * 2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    assert pytest.approx(float(basic_order.total_price), 1e-6) == price
    s = StorageMethodFactory(
        name="Vacuum",
        labour_multiplier=1.1,
        add_to_recipe_ingredients=[("banaan", "Fruitpap"), ("kiwi", "Fruitpap")],
    )
    price = 1.06 * ((1 + 0.3 + 0.1) * 2.5 * 0.05 + 1.1 * 3.5 * 0.07 + 4.5 * 0.13)
    assert basic_order.order.total_price == basic_order.total_price
    assert basic_order.order.total_vat == basic_order.total_vat
    assert (
        pytest.approx(basic_order.order.total_price_no_vat, 1e-6)
        == basic_order.total_price - basic_order.total_vat
    )
    assert pytest.approx(float(basic_order.total_price), 1e-6) == price

@pytest.mark.django_db
def test_single_unit_ingredient(basic_order):
    set_prices([("banaan", 2.5), ("kiwi", 0), ("appel",0)])
    ing_0 = basic_order.recipe.ingredients.all()[0]
    ing_0.amount_mass = 0
    ing_0.amount_units = 10
    ing_0.ingredient.price_unit = None
    ing_0.save()
    assert pytest.approx(float(basic_order.total_price), 1e-3) == 25.0 * 1.06


@pytest.mark.django_db
def test_vat_on_order(basic_order: OrderRecipe):
    set_prices([("banaan", 2.5), ("kiwi", 3.5), ("appel", 4.5)])
    basic_order.amount_multiplier = 100
    vat = 0.06 * (2.5 * 0.05 + 3.5 * 0.07 + 4.5 * 0.13)
    assert pytest.approx(float(basic_order.total_vat), 1e-6) == vat * 100


@pytest.mark.django_db
def test_next_stage():
    order = OrderFactory()
    assert order.status == OrderStatus.IN_CART
    order.advance_stage()
    assert order.status == OrderStatus.ORDERED


@pytest.mark.django_db
def test_fixate_order(basic_order: OrderRecipe):
    basic_order.fixate_recipe()
    print(basic_order.fixed_recipe)
    assert len(basic_order.fixed_recipe.split("\n")) == 4


@pytest.mark.django_db
def test_confirm_order():
    user = UserFactory()
    order = OrderFactory(user_id=user.id)
    assert order.status == OrderStatus.IN_CART
    c = Client()
    delivery = datetime(2021, 5, 17)
    delivery_str = delivery.strftime("%Y-%m-%d")
    notes = "These are notes"
    c.post("/login", data={"username": user.username, "password": user.password})
    r = c.post(
        f"/order/confirm_order/{order.id}", data={"delivery_date": delivery_str, "notes": notes},
    )
    order.refresh_from_db()
    assert order.status == OrderStatus.IN_CART
    assert order.delivery_date == delivery
    assert order.notes == notes
    c.post(
        f"/order/confirm_order/{order.id}?advance_stage=1",
        data={"delivery_date": delivery_str, "notes": notes},
    )
    order.refresh_from_db()
    assert order.status == OrderStatus.IN_CART
    assert order.delivery_date == delivery
    assert order.notes == notes
