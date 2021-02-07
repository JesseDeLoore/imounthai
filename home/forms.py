# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from django.forms import HiddenInput, CharField
from verify_email.email_handler import send_verification_email


class UserAccountForm(PopRequestMixin, CreateUpdateAjaxMixin, UserCreationForm):
    username = CharField(label=_("Email"))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password1', 'password2', 'username']
        widgets = {"username": HiddenInput()}

    def is_valid(self):
        if super().is_valid():
            inactive_user = send_verification_email(self.request, self)