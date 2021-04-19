from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy

from shop.forms import TemporaryRecipeForm, RecipeIngredientFormSet
from shop.models import Order, OrderStatus, OrderRecipe, Recipe


def _get_cart_order(user: User):
    return Order.objects.filter(user=user, status=OrderStatus.IN_CART).all()


def shopping_cart(request: HttpRequest):
    orders = _get_cart_order(request.user)
    return render(request, "shop/cart.html", context={"orders": orders})


class TemporaryRecipeCreateView(BSModalCreateView):
    """Inspired by https://dev.to/zxenia/django-inline-formsets-with-class-based-views-and-crispy-forms-14o6"""

    template_name = 'shop/temp_recipe_modal.html'
    form_class = TemporaryRecipeForm
    success_message = ''
    success_url = reverse_lazy("cart")

    def get_context_data(self, **kwargs):
        data = super(TemporaryRecipeCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['ingredients'] = RecipeIngredientFormSet(self.request.POST)
        else:
            data['ingredients'] = RecipeIngredientFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ingredients = context['ingredients']
        with transaction.atomic():
            self.object = form.save()
            if ingredients.is_valid():
                ingredients.instance = self.object
                ingredients.save()
        return super(TemporaryRecipeCreateView, self).form_valid(form)


class TemporaryRecipeUpdateView(BSModalUpdateView):
    model = Recipe
    template_name = 'shop/temp_recipe_modal.html'
    form_class = TemporaryRecipeForm
    success_message = ''
    success_url = reverse_lazy("cart")


    def get_context_data(self, **kwargs):
        data = super(TemporaryRecipeUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['ingredients'] = RecipeIngredientFormSet(self.request.POST)
        else:
            data['ingredients'] = RecipeIngredientFormSet(self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ingredients = context['ingredients']
        with transaction.atomic():
            self.object = form.save()
            if ingredients.is_valid():
                ingredients.instance = self.object
                ingredients.save()
        return super(TemporaryRecipeUpdateView, self).form_valid(form)


