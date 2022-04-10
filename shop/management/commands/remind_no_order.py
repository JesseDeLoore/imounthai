import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Max, F
from django.template.loader import get_template

from shop.models import short, OrderStatus
from html2text import html2text

class Command(BaseCommand):
    help = "Remind all users that haven't ordered yet they should, by mail"

    def add_arguments(self, parser):
        parser.add_argument('--dryrun', action="store_false")  # default false

    def handle(self, *args, **options):
        CUTOFF_DATE = pd.Timestamp.now("CET").floor("D") - pd.Timedelta(days=3)
        user_set = (User.objects.exclude(shop_preferences__allow_reminders=False) # Want to receive mails
                    .filter(email__isnull=False).filter(email__contains='@') # Need a valid e-mail
                    .annotate(last_order=Max("orders__delivery_date")) # Get the latest order delivery date
                    .exclude(shop_preferences__last_reminder__isnull=False, last_order__lte=F("shop_preferences__last_reminder")) # No mail has been sent yet about this
                    .filter(last_order__lte= CUTOFF_DATE) # Latest delivery is long enough ago
                    )
        for user in user_set:
            last_order = user.orders.order_by("-delivery_date").first()
            if not last_order:
                continue
            last_order = ", ".join(short(recipe.recipe.name) for recipe in last_order.ordered_recipes.all())
            cart_order = user.orders.filter(status=OrderStatus.IN_CART).all()
            subj = f"Immuunthai: Niets vergeten deze week ?"
            body = get_template("shop/email/no_order_this_week.html")
            html_body = body.render({"user": user, "cart":cart_order, "last_order": last_order, "domain":settings.BASE_URL})
            text_body = html2text(html_body)
            if not options["dryrun"]:
                user.email_user(subject=subj, message=text_body, html_message=html_body)
                prefs = user.shop_preferences.first()
                prefs.last_reminder = pd.Timestamp.now("CET")
                prefs.save()
            self.stdout.write(f"Sending mail to {user=}\n{last_order=}\n{cart_order=}\n{text_body}")
