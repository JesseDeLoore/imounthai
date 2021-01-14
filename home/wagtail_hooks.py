# -*- coding: utf-8 -*-
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin import views
from django_ses.views import dashboard
from social_django.models import Association, UserSocialAuth
from django.urls import path

from wagtail.core import hooks


class SocialAssociationAdmin(ModelAdmin):
    model = Association
    add_to_settings_menu = True


class UserSocialAuthAdmin(ModelAdmin):
    model = UserSocialAuth
    add_to_settings_menu = True


modeladmin_register(SocialAssociationAdmin)
modeladmin_register(UserSocialAuthAdmin)


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        path('django-ses/', dashboard, name='Django SES Stats'),
    ]
