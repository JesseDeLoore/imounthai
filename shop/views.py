import datetime
from collections import defaultdict
from random import randrange

from bootstrap_modal_forms.generic import (
    BSModalCreateView,
    BSModalUpdateView,
    BSModalDeleteView,
)
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView

from shop.forms import (
    TemporaryRecipeForm,
    RecipeIngredientFormSet,
    OrderRecipeForm,
    OrderForm,
    OrderRecipeCreateForm,
)
from shop.models import Order, OrderStatus, OrderRecipe, Recipe


def _get_cart_order(user: User):
    return Order.objects.filter(user=user, status=OrderStatus.IN_CART).all()


def _get_user_order(user: User):
    return Order.objects.filter(user=user)


def shopping_cart(request: HttpRequest):
    orders = _get_cart_order(request.user)
    open_modal = request.GET.get("open_modal")
    if open_modal:
        return render(
            request, "shop/cart.html", context={"orders": orders, "open_recipe": int(open_modal)},
        )
    return render(request, "shop/cart.html", context={"orders": orders})


def order_history(request: HttpRequest):
    orders = _get_user_order(request.user)
    status_orders = {
        name: orders.filter(status=status).all() for status, name in OrderStatus.choices[1:]
    }

    return render(request, "shop/history.html", context={"status_orders": status_orders})


class RecipeRemoveView(BSModalDeleteView):
    success_message = ""
    model = OrderRecipe
    success_url = reverse_lazy("shopping_cart")


class OrderRecipeCreateView(BSModalCreateView):
    success_message = ""
    success_url = reverse_lazy("shopping_cart")
    model = OrderRecipe
    template_name = "shop/create_orderrecipe_modal.html"
    form_class = OrderRecipeCreateForm


class OrderRecipeSetAmountView(BSModalUpdateView):
    success_message = ""
    model = OrderRecipe
    success_url = reverse_lazy("shopping_cart")
    template_name = "shop/order_quant_modal.html"
    form_class = OrderRecipeForm


class OrderUpdateView(BSModalUpdateView):
    success_message = ""
    model = Order
    success_url = reverse_lazy("order_history")
    template_name = "shop/update_order_modal.html"
    form_class = OrderForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        rv = super().form_valid(form)
        if self.request.GET.get("advance_stage"):
            self.object.advance_stage()
        return rv


def create_new_temp_recipe(request: HttpRequest, order, recipe):
    order = OrderRecipe.objects.get(pk=order)
    recipe = Recipe.objects.get(pk=recipe)
    rand_suffix = f"{randrange(16 ** 6):06x}"
    temp_recipe = recipe.create_temp_copy(f"-{request.user.username}-{rand_suffix}")
    order.recipe = temp_recipe
    order.save()
    return redirect(reverse("shopping_cart") + f"?open_modal={temp_recipe.id}")


class RecipeUpdateView(BSModalUpdateView):
    # Inspired by https://dev.to/zxenia/django-inline-formsets-with-class-based-views
    # -and-crispy-forms-14o6
    model = Recipe
    template_name = "shop/temp_recipe_modal.html"
    form_class = TemporaryRecipeForm
    success_message = ""
    success_url = reverse_lazy("shopping_cart")

    def get_context_data(self, **kwargs):
        data = super(RecipeUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data["ingredients"] = RecipeIngredientFormSet(self.request.POST, instance=self.object)
        else:
            data["ingredients"] = RecipeIngredientFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ingredients = context["ingredients"]
        with transaction.atomic():
            self.object = form.save()
            if ingredients.is_valid():
                ingredients.instance = self.object
                ingredients.save()
        return super(RecipeUpdateView, self).form_valid(form)


class RecipeListView(ListView):
    model = Recipe
    queryset = Recipe.objects.filter(is_temporary=False).all()
