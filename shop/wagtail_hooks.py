# -*- coding: utf-8 -*-
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from .models import *


class IngredientAdmin(ModelAdmin):
    model = Ingredient
    menu_label = "Ingredienten"
    menu_icon = "table"
    list_display = ["name", "purchase_price", "sell_price"]
    list_filter = ["name"]


class AllergenAdmin(ModelAdmin):
    model = Allergen
    menu_label = "Allergenen"
    menu_icon = "table"
    list_display = ["name", "code"]
    list_filter = ["name"]


class NurientAdmin(ModelAdmin):
    model = Nutrition
    menu_label = "Voedingsstoffen"
    menu_icon = "table"
    list_display = ["name", "scientific_name"]
    list_filter = ["name", "scientific_name"]


class RecipeAdmin(ModelAdmin):
    model = Recipe
    menu_label = "Recepten"
    menu_icon = "table"
    list_display = ["name", "is_temporary", "base_servings"]
    list_filter = ["name", "is_temporary"]


class OrderAdmin(ModelAdmin):
    model = Order
    menu_label = "Order"
    menu_icon = "table"
    list_display = ["user", "status", "delivery_date"]
    list_filter = ["user", "status", "delivery_date"]


class CustomOrderLineAdmin(ModelAdmin):
    model = OrderCustomLine
    menu_label = "Speciale orderlijn"
    menu_icon = "table"
    list_display = ["quantity", "unit_price", "description", "order"]
    list_filter = ["quantity", "unit_price", "description", "order"]

class ProcessMethodAdmin(ModelAdmin):
    model = ProcessMethod
    menu_label = "Verwerkings Methode"
    menu_icon = "list-ul"

class StorageMethodAdmin(ModelAdmin):
    model = StorageMethod
    menu_label = "Type opslag"
    menu_icon = "list-ul"


class ShopGroup(ModelAdminGroup):
    menu_label = 'Shop'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (OrderAdmin, CustomOrderLineAdmin, RecipeAdmin, IngredientAdmin, AllergenAdmin,
             NurientAdmin, ProcessMethodAdmin, StorageMethodAdmin)




modeladmin_register(ShopGroup)
