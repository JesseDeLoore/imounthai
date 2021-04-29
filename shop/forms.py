# -*- coding: utf-8 -*-
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Fieldset, ButtonHolder, Submit
from django import forms
from django.forms import inlineformset_factory

from home.utils import Formset
from shop.models import Recipe, RecipeIngredient, OrderRecipe


class IngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ("ingredient", "amount_mass", "amount_volume")


RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient, form=IngredientForm,
    fields=['ingredient', "amount_mass", "amount_volume"], extra=0, can_delete=True,
)


class TemporaryRecipeForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ["sell_price", ]

    def __init__(self, *args, **kwargs):
        super(TemporaryRecipeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field("name", readonly=True),
                Field("base_servings", type="hidden"),
                Field("is_temporary", type="hidden"),
                Fieldset('Ingredienten', Formset('ingredients')),
                ButtonHolder(Submit('submit', 'Opslaan')),
            )
        )


class OrderRecipeForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = OrderRecipe
        fields = ["amount_multiplier", ]

    def __init__(self, *args, **kwargs):
        super(OrderRecipeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field("amount_multiplier"),
                ButtonHolder(Submit('submit', 'Opslaan')),
            )
        )