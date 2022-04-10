import re
from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest
from django.core.management import call_command

from shop.models import OrderStatus


@pytest.mark.django_db
@patch("shop.management.commands.remind_no_order.User.email_user")
class TestRemindNoOrder:
    @pytest.fixture(autouse=True)
    def prep_cart(self, basic_order):
        order = basic_order.order
        assert order.user.shop_preferences.first().allow_reminders
        assert not order.user.shop_preferences.first().last_reminder
        self.order = order
        self.out = StringIO()

    def test_no_history(self, send_mail):
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_not_called()
        assert not self.order.user.shop_preferences.first().last_reminder
        assert not self.out.getvalue()

    def test_last_order_recent(self, send_mail):
        self.order.delivery_date = pd.Timestamp.now("CET") - pd.Timedelta(days=2)
        self.order.save()
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_not_called()
        assert not self.order.user.shop_preferences.first().last_reminder
        assert not self.out.getvalue()

    def test_no_permission(self, send_mail):

        self.order.delivery_date = pd.Timestamp.now("CET") - pd.Timedelta(days=4)
        preferences = self.order.user.shop_preferences.first()
        preferences.allow_reminders = False
        preferences.save()
        self.order.save()
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_not_called()
        assert not preferences.last_reminder
        assert not self.out.getvalue()

    def test_no_valid_email(self, send_mail):

        self.order.delivery_date = pd.Timestamp.now("CET") - pd.Timedelta(days=4)
        self.order.user.email = "my.name"
        self.order.user.save()
        self.order.save()
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_not_called()
        assert not self.order.user.shop_preferences.first().last_reminder
        assert not self.out.getvalue()

    def test_already_reminded(self, send_mail):

        self.order.delivery_date = pd.Timestamp.now("CET") - pd.Timedelta(days=4)
        preferences = self.order.user.shop_preferences.first()
        now = pd.Timestamp.now("CET") - pd.Timedelta(days=2)
        preferences.last_reminder = now
        preferences.save()
        self.order.save()
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_not_called()
        assert preferences.last_reminder == now
        assert not self.out.getvalue()


    def test_last_order_before_threshold_with_cart(self, send_mail):

        self.order.delivery_date = pd.Timestamp.now("CET") - pd.Timedelta(days=4)
        self.order.save()
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_called_once()
        assert self.order.user.shop_preferences.first().last_reminder
        assert re.match((
     r"""Sending mail to user=<User: .*>
last_order='Fruitpap'
cart_order\=<QuerySet \[<Order: .*IC.*]>
\s*Beste .*\s*
We hebben deze week nog geen bestelling ontvangen van jou.\s*
Er zit nog een bestelling in \[je winkelmandje]\(https:\/\/imounthai-
dev.sennac.be\/shop\/cart\/\).\s*
1.00 x Fruitpap\s*
Hopelijk tot snel!\s*
Immuunthai\s*"""), self.out.getvalue())

    def test_last_order_before_threshold_with_history(self, send_mail):
        self.order.delivery_date = pd.Timestamp.now("CET") - pd.Timedelta(days=4)
        self.order.status = OrderStatus.ORDERED
        self.order.save()
        call_command("remind_no_order", stdout=self.out, sendmails=True)

        send_mail.assert_called_once()
        assert self.order.user.shop_preferences.first().last_reminder
        print(self.out.getvalue())
        assert re.match((
            r"""Sending mail to user=<User: .*>
last_order='Fruitpap'
cart_order\=<QuerySet \[]>
\s*Beste .*\s*
We hebben deze week nog geen bestelling ontvangen van jou.\s*
Je bestelde vorige keer Fruitpap Je kan \[hier]\(https://imounthai-
dev.sennac.be/shop/order/history\) je bestelgeschiedenis bekijken en opnieuw
bestellen\s*
Hopelijk tot snel!\s*
Immuunthai\s*"""), self.out.getvalue())




