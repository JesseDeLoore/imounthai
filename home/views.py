# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import UserAccountCreateForm, UpdateProfileForm
from bootstrap_modal_forms.generic import BSModalCreateView


class UserAccountCreateView(BSModalCreateView):
    template_name = "registration/create_user_account.html"
    form_class = UserAccountCreateForm
    success_message = ""
    success_url = "/"


class UserEditView(UpdateView):
    model = User
    template_name = "registration/user_account.html"
    form_class = UpdateProfileForm
    success_message = ""
    success_url = reverse_lazy("edit_user")


def privacy_policy(request):
    return render(request, "home/privacy_policy.html")
