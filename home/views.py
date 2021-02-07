# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from .forms import UserAccountForm
from bootstrap_modal_forms.generic import BSModalCreateView


class UserAccountCreateView(BSModalCreateView):
    template_name = 'registration/create_user_account.html'
    form_class = UserAccountForm
    success_message = ''
    success_url = '/'
