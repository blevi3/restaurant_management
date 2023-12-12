from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Menuitem, Cart, CartItem, Coupons, Table, Reservation, Qr_code_reads
from ..forms import CouponForm  
from .menu_views import get_recommendations  
from django.conf import settings  
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta
import pytz
from django.http import JsonResponse

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user, is_delivered=0)

    update_table(request, cart)

    if cart.discount == 0 and request.method == 'POST':
        handle_coupon(request, cart)

    calculate_total_price(cart)
    recommendations = get_recommendations([item.item_id for item in CartItem.objects.filter(cart=cart)])

    context = {
        'recommendations': [Menuitem.objects.get(id=id) for id in recommendations],
        'cart_items': CartItem.objects.filter(cart=cart),
        'final_price': cart.amount_to_be_paid,
        'ordered': cart.ordered,
        'paid': cart.is_paid,
        'cartid': cart.id,
        'discount': get_discount_amount(cart),
        'coupon': 1 if cart.discount else 0,
        'reduced_priced_product': Coupons.objects.get(id=cart.discount).product if cart.discount else None,
        'publishable_key': settings.STRIPE_TEST_PUBLISHABLE_KEY,
        'table': cart.table,
        'tables': Table.objects.all(),
    }

    return render(request, 'cart.html', context)

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, _ = Cart.objects.get_or_create(user=request.user, is_delivered=0)

    quantity = handle_cart_item(cart, item, request.GET.get('foodComment', ''))
    print("quan1",quantity)
    calculate_total_price(cart)
    response_data = {
        'message': 'Item added to the cart successfully',
        'item_name': item.name,
        'item_price': item.price,
        'quantity': quantity,
    }

    return JsonResponse(response_data)

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if not cart_item.cart.ordered and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.final_price = cart_item.item.price * cart_item.quantity
        cart_item.save()
    else:
        if cart_item.cart.applied_coupon_type:
            cart_item.cart.discount = 0
            cart_item.cart.applied_coupon_type = None
            cart_item.cart.save()
        cart_item.delete()
    
    calculate_total_price(cart_item.cart)
    return redirect('cart')

@login_required
def trash_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if not cart_item.cart.ordered:
        if cart_item.cart.applied_coupon_type:
            cart_item.cart.discount = 0
            cart_item.cart.applied_coupon_type = None
            cart_item.cart.save()
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
    calculate_total_price(cart)
    
    return redirect('cart')

@login_required  
def order(request, id):
    cart = Cart.objects.get(pk = id)
    calculate_total_price(cart)
    cart.ordered = 1
    cart.order_time = datetime.now(pytz.timezone('Europe/Budapest'))
    cart.save()
    Qr_code_reads.objects.filter(user=request.user, ordered=0).update(ordered=1)
    return redirect('cart')

@staff_member_required
def order_paid(request, id):
    cart = Cart.objects.get(pk = id)
    cart.ordered = 1
    cart.is_paid = 1
    cart.save()
    return redirect('cart') 

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
    
    calculate_total_price(cart)
    return redirect('cart')


@login_required
def handle_scanned_qr(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user, ordered=0, is_delivered=0)
    table = request.GET.get('table')

    if not table:
        return JsonResponse({'error': 'Table not specified'})

    try:
        table_obj = Table.objects.get(name=table)
    except Table.DoesNotExist:
        return JsonResponse({'error': 'Invalid table'})
    
    reservation = None
    try:
        current_time = timezone.now().astimezone(pytz.timezone('Europe/Budapest'))
        from django.db.models import F

        reservations = Reservation.objects.filter(
            table=table_obj,
            taken=0,
            start_time__lte=F('start_time') + timedelta(minutes=20),
            start_time__gte=F('start_time') - timedelta(minutes=20)
        ).order_by('start_time')
        print(reservations)
        if reservations.exists():
            reservation = reservations.first()

        right_user = reservation and reservation.user == user


        reservation_start_time = reservation.start_time

        # Create a fixed timezone-aware datetime object for 'Europe/Budapest'
        budapest_timezone = pytz.timezone('Europe/Budapest')
        fixed_budapest_time = datetime.now(budapest_timezone)

        # Set the time component to match the reservation time
        fixed_budapest_time = fixed_budapest_time.replace(hour=reservation_start_time.hour, minute=reservation_start_time.minute, second=0, microsecond=0)

        reserved_hold_time_ended = fixed_budapest_time + timedelta(minutes=20) < datetime.now(budapest_timezone)

        print("reservation start", fixed_budapest_time + timedelta(minutes=20))
        print(reservation)
        print("current time", datetime.now(budapest_timezone))
        print("reservation ended", reserved_hold_time_ended)


        reservation_taken = reservation and reservation.taken

        qr_read_within_1hour = Qr_code_reads.objects.filter(
            user=user,
            table=table_obj,
            read_time__gte=datetime.now(pytz.timezone('Europe/Budapest')) - timedelta(minutes=60),
            finalized=1
        ).exists()

    except Reservation.DoesNotExist:
        right_user = False
        reserved_hold_time_ended = False
        reservation_taken = False
        qr_read_within_1hour = False

    if reservation and (right_user or reservation_taken or qr_read_within_1hour):
        cart.table = table
        reservation.taken = 1
        reservation.save()
        cart.save()

        if not Qr_code_reads.objects.filter(user=user).exists():
            Qr_code_reads.objects.create(user=user, table=table_obj, read_time=timezone.now(), finalized=1)
        if Qr_code_reads.objects.filter(user=user, finalized=0).exists():
            Qr_code_reads.objects.filter(user=user, finalized=0).update(finalized=1)
            Qr_code_reads.objects.create(user=user, table=table_obj, read_time=timezone.now(), finalized=1)
        print('reserved for user')
        return redirect('order')

    elif reservation and not reserved_hold_time_ended and not reservation_taken:
        print('reserved')
        reservation_end_time = reservation.start_time + timedelta(minutes=20)
        messages.error(request, f'Table reserved until: {reservation_end_time}')
        return JsonResponse({'error': f'Table reserved until: {reservation_end_time}'})
    else:
        print('no reservation')
        cart.table = table
        cart.save()
        return redirect('order')

def update_table(request, cart):
    table = request.POST.get('table')
    if table:
        cart.table = table
        cart.save()

def handle_coupon(request, cart):
    coupon_form = CouponForm(request.POST)
    if coupon_form.is_valid():
        code = coupon_form.cleaned_data['code']
        try:
            coupon = Coupons.objects.get(code=code)
            apply_coupon(request, cart, request.user, coupon)
        except Coupons.DoesNotExist:
            messages.error(request, 'Invalid coupon code')

def apply_coupon(request, cart, user, coupon):
    if coupon.user_id in [0, user.id]:
        if cart.applied_coupon_type:
            messages.error(request, f'You already applied a {cart.applied_coupon_type} coupon.')
        else:
            items = CartItem.objects.filter(cart=cart)
            allowed_product = Menuitem.objects.filter(name=coupon.product).first()

            if coupon.coupon_type == 'percentage' and allowed_product:
                eligible_items = items.filter(item=allowed_product)
                if eligible_items.exists():
                    percentage_discount = coupon.percentage
                    print(percentage_discount)
                    for item in eligible_items:
                        print(item.total_price)
                        item.total_price -= (percentage_discount * item.total_price / 100)
                        item.save()
                    cart.discount = coupon.id
                    cart.applied_coupon_type = 'percentage'
                    messages.success(request, f'{percentage_discount}% coupon "{coupon.code}" applied!')

            elif coupon.coupon_type == 'fixed':
                cart.amount_to_be_paid -= coupon.fixed_amount
                cart.discount = coupon.id
                cart.applied_coupon_type = 'fixed'
                cart.reduced_price = cart.amount_to_be_paid
                cart.save()
                messages.success(request, f'Fixed amount coupon "{coupon.code}" applied!')

    else:
        messages.error(request, 'Invalid coupon type.')

    cart.save()


def handle_cart_item(cart, item, comment):
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not cart.ordered and not cart.is_delivered:
        cart_item.quantity += 1
        cart_item.total_price = item.price
        cart_item.final_price = item.price * cart_item.quantity
        cart_item.comment = comment
        cart_item.save()
    return cart_item.quantity

def calculate_total_price(cart):
    total_price = sum(cart_item.final_price for cart_item in CartItem.objects.filter(cart=cart))
    total_price -= get_discount_amount(cart)
    cart.amount_to_be_paid = max(total_price, cart.reduced_price)
    cart.save()

def get_discount_amount(cart):
    discount = 0
    if cart.discount:
        if cart.applied_coupon_type == 'fixed':
            discount = Coupons.objects.get(id=cart.discount).fixed_amount
        elif cart.applied_coupon_type == 'percentage':
            percentage_coupon = Coupons.objects.get(id=cart.discount)
            eligible_item = Menuitem.objects.filter(name=percentage_coupon.product).first()
            eligible_item_total_price = CartItem.objects.get(cart=cart, item=eligible_item).final_price
            print(eligible_item_total_price)
            discount = eligible_item_total_price * percentage_coupon.percentage / 100
    return discount
