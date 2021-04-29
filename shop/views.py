import datetime
from random import randrange

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, \
    BSModalDeleteView
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse

from shop.forms import TemporaryRecipeForm, RecipeIngredientFormSet, OrderRecipeForm
from shop.models import Order, OrderStatus, OrderRecipe, Recipe


def _get_cart_order(user: User):
    return Order.objects.filter(user=user, status=OrderStatus.IN_CART).all()


def shopping_cart(request: HttpRequest):
    orders = _get_cart_order(request.user)
    open_modal = request.GET.get("open_modal")
    if open_modal:
        return render(request, "shop/cart.html",
                      context={"orders": orders, "open_recipe": int(open_modal)})
    return render(request, "shop/cart.html", context={"orders": orders})


class RecipeRemoveView(BSModalDeleteView):
    success_message = ""
    model = OrderRecipe
    success_url = reverse_lazy("shopping_cart")


class OrderRecipeUpdateView(BSModalUpdateView):
    success_message = ""
    model = OrderRecipe
    success_url = reverse_lazy("shopping_cart")
    template_name = 'shop/order_quant_modal.html'
    form_class = OrderRecipeForm


def create_new_temp_recipe(request:HttpRequest, order, recipe):
    order = OrderRecipe.objects.get(pk=order)
    recipe = Recipe.objects.get(pk=recipe)
    rand_suffix = f'{randrange(16 ** 6):030x}'
    temp_recipe = recipe.create_temp_copy(f"-{request.user.username}-{rand_suffix}")
    order.recipe = temp_recipe
    order.save()
    return redirect(reverse("shopping_cart")+f"?open_modal={temp_recipe.id}")




class RecipeUpdateView(BSModalUpdateView):
    # Inspired by https://dev.to/zxenia/django-inline-formsets-with-class-based-views
    # -and-crispy-forms-14o6
    model = Recipe
    template_name = 'shop/temp_recipe_modal.html'
    form_class = TemporaryRecipeForm
    success_message = ''
    success_url = reverse_lazy("shopping_cart")

    def get_context_data(self, **kwargs):
        data = super(RecipeUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['ingredients'] = RecipeIngredientFormSet(self.request.POST, instance=self.object)
        else:
            data['ingredients'] = RecipeIngredientFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ingredients = context['ingredients']
        with transaction.atomic():
            self.object = form.save()
            if ingredients.is_valid():
                ingredients.instance = self.object
                ingredients.save()
        return super(RecipeUpdateView, self).form_valid(form)
