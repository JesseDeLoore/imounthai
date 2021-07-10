# -*- coding: utf-8 -*-
import datetime

from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Fieldset, ButtonHolder, Submit
from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import DateInput

from home.utils import Formset
from shop.models import Recipe, RecipeIngredient, OrderRecipe, Order


def next_delivery_day():
    now = datetime.datetime.now()
    # Before saturday
    if now.weekday() < 4:
        # return next week monday
        return (now - datetime.timedelta(days=now.weekday() - 7)).date()
    # return monday after that
    return (now - datetime.timedelta(days=now.weekday() - 14)).date()


class IngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ("ingredient", "amount_mass", "amount_volume")


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=IngredientForm,
    fields=["ingredient", "amount_mass", "amount_volume"],
    extra=0,
    min_num=0,
    can_delete=True,
)


class TemporaryRecipeForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ["sell_price"]

    def __init__(self, *args, **kwargs):
        super(TemporaryRecipeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Div(
                Field("name", readonly=True),
                Field("base_servings", type="hidden"),
                Field("is_temporary", type="hidden"),
                Fieldset("Ingredienten", Formset("ingredients")),
                ButtonHolder(Submit("opslaan", "Opslaan")),
            )
        )


class OrderForm(BSModalModelForm):
    class Meta:
        model = Order
        fields = ["notes", "delivery_date"]
        widgets = {
            "delivery_date": DateInput(
                attrs={
                    "type": "date",
                    "min": next_delivery_day(),
                    "max": next_delivery_day() + datetime.timedelta(days=7 * 6),
                    "step": "7",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Div(
                Field("delivery_date"),
                Field("notes"),
                ButtonHolder(Submit("bestellen", "Bestellen")),
            )
        )


class OrderRecipeForm(BSModalModelForm):
    class Meta:
        model = OrderRecipe
        fields = [
            "amount_multiplier",
        ]

    def __init__(self, *args, **kwargs):
        super(OrderRecipeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Div(Field("amount_multiplier"), ButtonHolder(Submit("opslaan", "Opslaan")),)
        )


class OrderRecipeCreateForm(BSModalModelForm):
    class Meta:
        model = OrderRecipe
        fields = [
            "amount_multiplier",
            "recipe",
            "order",
        ]

    def __init__(self, *args, **kwargs):
        super(OrderRecipeCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Div(
                Field("recipe", type="hidden"),
                Field("order", type="hidden"),
                Field("amount_multiplier"),
                ButtonHolder(Submit("opslaan", "Opslaan")),
            )
        )
