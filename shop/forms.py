# -*- coding: utf-8 -*-
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from django import forms
from django.forms import inlineformset_factory

from shop.models import Recipe, RecipeIngredient


class IngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ("ingredient",)


RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient, form=IngredientForm,
    fields=['ingredient'], extra=0, can_delete=True
)


class TemporaryRecipeForm(PopRequestMixin, CreateUpdateAjaxMixin):
    class Meta:
        model = Recipe
        fields = ["id", "ingredients"]
