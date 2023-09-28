from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Menuitem, Cart, CartItem, Coupons, Table
from ..forms import CouponForm  
from .menu_views import get_recommendations  
from django.conf import settings  


@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user, is_delivered=0)
    discount = 0
    have_coupon = 0
    final_price = 0
    cart_items = CartItem.objects.filter(cart=cart)
    cart_item_ids = [item.item_id for item in cart_items]
    reduced_priced_product = None

    if cart.discount == 0 and request.method == 'POST':
        coupon_form = CouponForm(request.POST)
        table = request.POST.get('table')
        if table:
            cart.table = table
            cart.save()
        if coupon_form.is_valid():
            code = coupon_form.cleaned_data['code']
            try:
                coupon = Coupons.objects.get(code=code)

                if coupon.user_id in [0, request.user.id]:
                    if cart.applied_coupon_type:
                        messages.error(request, f'You already applied a {cart.applied_coupon_type} coupon.')
                    else:
                        items = CartItem.objects.filter(cart=cart)
                        allowed_product = Menuitem.objects.filter(name=coupon.product).first()

                        if coupon.coupon_type == 'percentage' and allowed_product:
                            eligible_items = items.filter(item=allowed_product)
                            if eligible_items.exists():
                                percentage_discount = coupon.percentage
                                for item in eligible_items:
                                    item.total_price -= (percentage_discount * item.total_price / 100)
                                    item.save()
                                cart.discount = coupon.id
                                cart.applied_coupon_type = 'percentage'
                                cart.save()
                                messages.success(request, f'{percentage_discount}% coupon "{coupon.code}" applied!')

                        elif coupon.coupon_type == 'fixed':
                            cart.amount_to_be_paid -= coupon.fixed_amount
                            cart.discount = coupon.id
                            cart.applied_coupon_type = 'fixed'
                            cart.reduced_price = cart.amount_to_be_paid
                            discount = coupon.fixed_amount
                            cart.save()
                            messages.success(request, f'Fixed amount coupon "{coupon.code}" applied!')

                else:
                    messages.error(request, 'Invalid coupon type.')

            except Coupons.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')
            else:
                cart.save()

    if cart.discount:
        cart_coupon = Coupons.objects.filter(id=cart.discount).first()
        coupon_menuitem = Menuitem.objects.filter(name=cart_coupon.product).first()
        original_amount = CartItem.objects.filter(cart=cart, item=coupon_menuitem).first()
        if original_amount:
            discount = original_amount.final_price - original_amount.total_price * original_amount.quantity
        else:
            cart_coupon = 0

    final_price = sum(cart_item.quantity * cart_item.total_price for cart_item in cart_items)
    cart.amount_to_be_paid = final_price if cart.reduced_price == 0 or final_price <= cart.reduced_price else cart.reduced_price
    cart.save()

    recommendations = get_recommendations(cart_item_ids)
    recom = [Menuitem.objects.get(id=id) for id in recommendations]

    if cart.discount:
        if cart.applied_coupon_type == 'fixed':
            discount = Coupons.objects.get(id=cart.discount).fixed_amount
        have_coupon = 1
        reduced_priced_product = Coupons.objects.get(id=cart.discount).product

    tables = Table.objects.all() 
    return render(request, 'cart.html', {
        'recommendations': recom,
        'cart_items': cart_items,
        'final_price': cart.amount_to_be_paid,
        'ordered': cart.ordered,
        'paid': cart.is_paid,
        'cartid': cart.id,
        'discount': discount,
        'coupon': have_coupon,
        'reduced_priced_product': reduced_priced_product,
        'publishable_key': settings.STRIPE_TEST_PUBLISHABLE_KEY,
        'table': cart.table,
        'tables': tables,
    })


@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user, is_delivered=0)
    
    if not created and not cart.ordered:
        try:
            cart_item = CartItem.objects.get(cart=cart, item=item)
            cart_item.quantity += 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, item=item, quantity=1, final_price=item.price, total_price=item.price )
    
    return redirect('order')


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if not cart_item.cart.ordered and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.final_price = cart_item.item.price * cart_item.quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')



@login_required
def trash_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if not cart_item.cart.ordered:
        cart_item.delete()
    
    return redirect('cart')



@login_required
def empty_cart(request):
    carts = Cart.objects.filter(user=request.user, ordered=0)
    for cart in carts:
        if not cart.ordered:
            cart.delete()
    
    return redirect('cart')



@login_required
def add_to_cart_from_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user, is_delivered=0)
    
    if not created and not cart.ordered:
        try:
            cart_item = CartItem.objects.get(cart=cart, item=item)
            cart_item.quantity += 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, item=item, quantity=1, final_price=item.price, total_price=item.price)
    
    return redirect('cart')




def cart_delivered(request, id):
    cart = Cart.objects.get(pk = id)
    if cart.orderd == 1:
        cart.is_delivered = 1
        cart.save()
    return redirect('all_orders')


@login_required
def add_recom_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user, is_delivered=0)
    
    if not created and not cart.ordered:
        try:
            cart_item = CartItem.objects.get(cart=cart, item=item)
            cart_item.quantity += 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, item=item, quantity=1, final_price=item.price, total_price=item.price)
    
    return redirect('cart')

