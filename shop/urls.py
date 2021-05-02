# -*- coding: utf-8 -*-
from django.urls import path, include

from shop.views import (
    RecipeListView,
    shopping_cart,
    OrderRecipeCreateView,
    create_new_temp_recipe,
    RecipeUpdateView,
    RecipeRemoveView,
    OrderRecipeSetAmountView,
    OrderUpdateView,
    order_history,
)

order_url_patterns = [
    path(
        "create_temp_recipe/<int:order>/<int:recipe>",
        create_new_temp_recipe,
        name="create_temp_recipe",
    ),
    path("update_temp_recipe/<int:pk>", RecipeUpdateView.as_view(), name="update_temp_recipe",),
    path("remove_recipe/<int:pk>", RecipeRemoveView.as_view(), name="remove_recipe",),
    path("set_order_amount/<int:pk>", OrderRecipeSetAmountView.as_view(), name="update_order_quant",),
    path("confirm/<int:pk>", OrderUpdateView.as_view(), name="confirm_order",),
    path("history", order_history, name="order_history"),
]

urlpatterns = [
    path("recipe", RecipeListView.as_view(), name="recipe_list"),
    path("cart/", shopping_cart, name="shopping_cart"),
    path("cart/add/<int:pk>", OrderRecipeCreateView.as_view(), name="add_to_cart"),
    path("order/", include(order_url_patterns)),
]
