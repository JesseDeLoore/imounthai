# -*- coding: utf-8 -*-
import datetime

from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Fieldset, ButtonHolder, Submit
from django import forms
from django.forms import inlineformset_factory, TextInput


from home.utils import Formset
from shop.models import Recipe, RecipeIngredient, OrderRecipe, Order, Ingredient


def next_delivery_day():
    now = datetime.datetime.now()
    # Before tuesday
    if now.weekday() < 1:
        # return this week friday
        return (now + datetime.timedelta(days=4 - now.weekday() )).date()
    # return next week tuesday
    return (now + datetime.timedelta(days=8 - now.weekday())).date()


class IngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ("ingredient", "amount_units", "amount_mass", "amount_volume")

    def __init__(self, *args, **kwargs):
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.fields["ingredient"].queryset = Ingredient.objects.filter(is_available=True)
        self.helper = FormHelper()
        self.helper.form_tag = False
        if not self.instance.ingredient:
            return
        if self.instance.ingredient.price_unit is not None:
            self.fields.pop("amount_units")
        if self.instance.ingredient.price_unit not in ("g", "kg"):
            self.fields.pop("amount_mass")
        if self.instance.ingredient.price_unit not in ("l", "ml"):
            self.fields.pop("amount_volume")


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=IngredientForm,
    #fields=["ingredient", "amount_mass", "amount_volume", "amount_units"],
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
                Fieldset("Ingredienten", Formset("ingredients", template="bootstrap/table_inline_formset.html")),
                ButtonHolder(Submit("opslaan", "Opslaan")),
            )
        )


class OrderForm(BSModalModelForm):
    class Meta:
        model = Order
        fields = ["notes", "delivery_date"]
        widgets = {
            "delivery_date": TextInput(
                attrs={
                    "type": "text",
                    "min": next_delivery_day().strftime("%Y-%m-%d"),
                    "max": (next_delivery_day() + datetime.timedelta(days=7 * 6)).strftime("%Y-%m-%d"),
                    "data-excluded": "0,1,3,4,6", # this is sunday 0 because of JS standard
                    "id": "delivery-date"
                })}



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
            Div(Field("amount_multiplier", step=0.25), ButtonHolder(Submit("opslaan", "Opslaan")),)
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
                Field("amount_multiplier", step=0.25),
                ButtonHolder(Submit("opslaan", "Opslaan")),
            )
        )
