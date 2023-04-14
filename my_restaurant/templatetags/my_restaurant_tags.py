from django import template
from django.shortcuts import get_object_or_404
from my_restaurant.models import Cart, CartItem

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_item_count(context):
    request = context['request']
    cart = get_object_or_404(Cart, user=request.user, is_delivered = 0)
    items = CartItem.objects.filter(cart_id = cart)
    count=0
    for item in items:
        count += item.quantity
    return count
