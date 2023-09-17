from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Menuitem, Cart, CartItem, Coupons 
from ..forms import CouponForm  
from .menu_views import get_recommendations  
from django.conf import settings  


@login_required
def cart(request):
    
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    discount_code = request.POST.get('discount_code')
    discount = 0
    have_coupon = 0
    cart_items = {}
    cart_item_ids = []
    final_price = 0
    original_amount = 0
    reduced_priced_product = None

    if cart.discount == 0:
        if request.method == 'POST':
            coupon_form = CouponForm(request.POST)
            if coupon_form.is_valid():
                code = coupon_form.cleaned_data['code']
                try:
                    coupon = Coupons.objects.get(code=code)

                    if coupon.user_id == 0 or coupon.user_id == request.user.id:
                        print("coupon: ",coupon.coupon_type)
                        # Check if the coupon is already applied
                        if cart.applied_coupon_type:
                            messages.error(request, f'You already applied a {cart.applied_coupon_type} coupon.')
                            return redirect('cart')

                        cart = Cart.objects.get(user=request.user, ordered=False)
                        items = CartItem.objects.filter(cart_id=cart.id)
                        if coupon.coupon_type == 'percentage':
                            print("coupon type: ",coupon.coupon_type)
                            allowed_product= Menuitem.objects.filter(name = coupon.product).first()
                            if allowed_product:
                                print(allowed_product)
                                eligible_items = items.filter(item=allowed_product)
                                
                                if eligible_items.exists():
                                    print(f'You can use this coupon for {eligible_items.count()} item(s).')
                                    cart_coupon = coupon.percentage
                                    print(cart_coupon)

                                    for item in eligible_items:
                                        print("item: ",item.item.name)
                                        item.total_price -= (coupon.percentage * item.total_price / 100)
                                        item.save()
                                    cart.discount = coupon.id
                                    cart.applied_coupon_type = 'percentage'
                                    cart.save()
                                    messages.success(request, f'{coupon.percentage}% coupon "{coupon.code}" applied!')
                            
                        elif coupon.coupon_type == 'fixed':
                            print("coupon type: ",coupon.coupon_type)
                            # Apply fixed amount coupon
                            
                            cart.amount_to_be_paid -= coupon.fixed_amount
                            print("cart amount: ",cart.amount_to_be_paid)
                            cart.discount = coupon.id
                            cart.applied_coupon_type = 'fixed'
                            cart.reduced_price = cart.amount_to_be_paid
                            discount = coupon.fixed_amount

                            cart.save()
                            messages.success(request, f'Fixed amount coupon "{coupon.code}" applied!')
                            
                    else:
                        messages.error(request, f'Invalid coupon type.')

                except Coupons.DoesNotExist:
                    messages.error(request, 'Invalid coupon code.')
            else:
                messages.error(request, 'Invalid coupon code.')
    else:
        messages.error(request, f'You already applied a {cart.applied_coupon_type} coupon!')

    cart.save()


    try:
        cart_coupon = Coupons.objects.filter(id=cart.discount).first()
        coupon_menuitem = Menuitem.objects.filter(name = cart_coupon.product).first()
        original_amount = CartItem.objects.filter(cart_id = cart.id).filter(item_id = coupon_menuitem.id).first()
        discount = original_amount.final_price - original_amount.total_price*original_amount.quantity
    except:
        cart_coupon = 0
    if not created:
        cart_items = CartItem.objects.filter(cart=cart)
        final_price = 0
        for cart_item in cart_items:
            final_price+=cart_item.quantity*cart_item.total_price
            cart_item_ids.append(cart_item.item_id)
        cart.amount_to_be_paid = final_price
        if cart.reduced_price !=0:
            if cart.amount_to_be_paid > cart.reduced_price:
                cart.amount_to_be_paid = cart.reduced_price
        cart.save()

    recommendations = get_recommendations(cart_item_ids)
    recom = []

    for id in recommendations:
        item = Menuitem.objects.filter(id=id)[0]
        recom.append(item)


    if cart.discount !=0:
        if cart.applied_coupon_type == 'fixed':
            discount = Coupons.objects.filter(id=cart.discount).first().fixed_amount
        have_coupon = 1
        reduced_priced_product = Coupons.objects.filter(id=cart.discount).first().product
    else:
        have_coupon = 0
            
    return render(request, 'cart.html', {'recommendations':recom,
                                         'cart_items': cart_items, 
                                         'final_price': cart.amount_to_be_paid, 
                                         'ordered': cart.ordered, 
                                         'paid': cart.is_paid, 
                                         'cartid': cart.id,
                                         'discount': discount,
                                         'coupon': have_coupon,
                                         'reduced_priced_product': reduced_priced_product,
                                         'publishable_key': settings.STRIPE_TEST_PUBLISHABLE_KEY})



@login_required()
def add_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    if not created:
        cart.save()
    if not cart.ordered:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()

        else:
            cart_item.quantity = 1
            cart_item.total_price = item.price * cart_item.quantity
            cart_item.final_price = item.price
            cart_item.save()
    
    return redirect('order')

@login_required
def remove_from_cart(request, cart_item_id):
    
    cart_item = CartItem.objects.get(id=cart_item_id)
    item = Menuitem.objects.get(id = cart_item.item_id)
    #cart_item.total_price = item.price
    cart = Cart.objects.filter(id = cart_item.cart_id ,ordered=0)
    if cart:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect(reverse('cart'))
@login_required
def trash_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart = Cart.objects.filter(id = cart_item.cart_id ,ordered=0)
    if cart:
        cart_item.delete()
    return redirect(reverse('cart'))
@login_required
def empty_cart(request):

    cart = Cart.objects.filter(user = request.user ,ordered=0)
    if cart:
        cart.delete()
    return redirect(reverse('cart'))
@login_required
def add_to_cart_from_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    if not created:
        cart.save()
    if not cart.ordered:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        cart_item.quantity += 1
        cart_item.final_price = item.price * cart_item.quantity
        cart_item.save()
    return redirect('cart')

def cart_delivered(request, id):
    cart = Cart.objects.get(pk = id)

    cart.is_delivered = 1
    cart.save()
    return redirect('all_orders')

@login_required 
def add_recom_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    if not created:
        cart.save()
    if not cart.ordered:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()
        else:
            cart_item.quantity = 1
            cart_item.total_price = item.price * cart_item.quantity
            cart_item.final_price = item.price
            cart_item.save()
    
    return redirect('cart')