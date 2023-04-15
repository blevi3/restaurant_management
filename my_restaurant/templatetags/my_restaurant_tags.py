from django import template
from django.shortcuts import get_object_or_404
from my_restaurant.models import Cart, CartItem, Menuitem
from django.urls import reverse
from django.utils.safestring import mark_safe

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

@register.simple_tag(takes_context=True)
def cart_preview(context):
    request = context['request']
    cart = get_object_or_404(Cart, user=request.user, is_delivered = 0)
    items = CartItem.objects.filter(cart_id = cart)
    item_names =[]
    for item in items:
        menuitem = Menuitem.objects.get(id = item.item_id)
        item_names.append(menuitem.name)
    preview_html = '<div class="cart_preview" style="display: none;">'



    for i in range(len(items)):
        preview_html += f'<p>{item_names[i]} - {items[i].quantity} x {items[i].total_price}</p>'

    preview_html += f'<a href="{reverse("cart")}">View cart</a>'
    preview_html += '</div>'

    return mark_safe(preview_html)
