from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.
from shop.models import Order, OrderStatus


def _get_cart_order(user: User):
    return Order.objects.filter(user=User, status=OrderStatus.IN_CART).all()


async def shopping_cart(request: HttpRequest):
    orders = _get_cart_order(request.user)
    return render(request, "shop/cart.html", context={"order": orders})
