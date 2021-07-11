# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, ButtonHolder, Submit
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from django.forms import HiddenInput, CharField, ModelForm, EmailField
from verify_email.email_handler import send_verification_email


class UserAccountCreateForm(PopRequestMixin, CreateUpdateAjaxMixin, UserCreationForm):
    username = CharField(label=_("Email"))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "password1", "password2", "username"]
        widgets = {"username": HiddenInput()}

    def is_valid(self):
        if super().is_valid():
            inactive_user = send_verification_email(self.request, self)


class UpdateProfileForm(ModelForm):
    username = CharField(required=True)
    email = EmailField(required=True)
    first_name = CharField(required=False)
    last_name = CharField(required=False)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_email(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise ValidationError(
                "This email address is already in use. " "Please supply a different email address."
            )
        return email

    def save(self, commit=True):
        user = super(UpdateProfileForm, self).save(commit=False)
        user.email = self.clean_email()
        user.username = user.email

        if commit:
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Field("email"),
            Field("first_name"),
            Field("last_name"),
            FormActions(Submit("opslaan", "Opslaan")),
        )
