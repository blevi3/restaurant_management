from django import template
from django.shortcuts import get_object_or_404
from my_restaurant.models import Cart, CartItem, Menuitem
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def active_order_count(context):
    request = context['request']
    
    paid_carts = Cart.objects.filter(is_paid=True, is_delivered=False, ordered = True)
    unpaid_carts = Cart.objects.filter(is_paid=False, is_delivered=False, ordered = True)
    active_orders = paid_carts.count() + unpaid_carts.count()
    return active_orders

@register.simple_tag(takes_context=True)
def cart_item_count(context):
    request = context['request']
    count=0
    if request.user.is_authenticated:
        try:
            #cart = get_object_or_404(Cart, user=request.user, is_delivered = 0)
            cart = Cart.objects.get(user = request.user, is_delivered = 0)
            items = CartItem.objects.filter(cart_id = cart)
            for item in items:
                count += item.quantity
        except Cart.DoesNotExist:
            pass
    return count

from ..views.cart_views import calculate_total_price
@register.simple_tag(takes_context=True)
def cart_preview(context):
    request = context['request']
    preview_html = ''
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user = request.user, is_delivered = 0)
            items = CartItem.objects.filter(cart_id=cart)
            item_names = [Menuitem.objects.get(id=item.item_id).name for item in items]

            preview_html = '<div class="cart_preview" style="display: none; z-index: 2;">'
            preview_html += '<div class="cart-items">'
            calculate_total_price(cart)
            total = 0
            for item in items:
                item_name = Menuitem.objects.get(id=item.item_id).name
                extras_price = sum(extra.price for extra in item.extras.all())
                item_total_price = item.final_price + extras_price
                total += item_total_price * item.quantity
                preview_html += f'<p>{item_name} - {item.quantity} x {item_total_price} Ft</p>'
            preview_html += '</div>'
            
            preview_html += f'<p class="cart-total">Total: {float(cart.amount_to_be_paid)} Ft</p>'
            
            preview_html += f'<a href="{reverse("cart")}">View cart</a>'
            preview_html += '</div>'
        except Cart.DoesNotExist:
            pass

    return mark_safe(preview_html)



@register.filter(name='calculate_original_price')
def calculate_original_price(item):
    return Menuitem.objects.get(id=item.item_id).price + item.get_extras_price()

@register.filter(name='calculate_original_total_price')
def calculate_original_total_price(item):
    return (Menuitem.objects.get(id=item.item_id).price + item.get_extras_price()) * item.quantity