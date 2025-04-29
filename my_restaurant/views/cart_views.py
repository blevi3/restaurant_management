from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Menuitem, Cart, CartItem, Coupons, Table, Reservation, Qr_code_reads, Extra
from ..forms import CouponForm  
from .menu_views import get_recommendations  
from django.conf import settings  
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta
import pytz
from django.http import JsonResponse
import json
from django.db.models import Count

@login_required
def cart(request):
    print("cart")
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
    if request.method == 'POST':

        if not request.body:
            return JsonResponse({'error': 'Empty request body'}, status=400)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in the request body'}, status=400)
        item = get_object_or_404(Menuitem, pk=item_id)
        print("item",item)
        cart, _ = Cart.objects.get_or_create(user=request.user, is_delivered=0)
        extras = data.get('extras', []) 

        quantity = handle_cart_item(cart, item, data.get('foodComment', ''), extras)

        calculate_total_price(cart)

        response_data = {
            'message': 'Item added to the cart successfully',
            'item_name': item.name,
            'item_price': item.price,
            'quantity': quantity,
        }

        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid method'}, status=400)


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if not cart_item.cart.ordered and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.final_price = (cart_item.total_price + cart_item.get_extras_price()) * cart_item.quantity
        cart_item.save()
    else:
        if cart_item.cart.applied_coupon_type:
            # Check if other items in the cart still have the same coupon
            items_with_coupon = CartItem.objects.filter(cart=cart_item.cart, item__name=cart_item.item.name ).exclude(id=cart_item.id)

            if items_with_coupon.exists():
                # If other items have the same coupon, do not remove it
                cart_item.delete()
            else:
                # Remove the coupon if no other items have it
                cart_item.cart.discount = 0
                cart_item.cart.applied_coupon_type = None
                cart_item.cart.save()
                cart_item.delete()
        else:
            cart_item.delete()

    calculate_total_price(cart_item.cart)
    return redirect('cart')

@login_required
def trash_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if not cart_item.cart.ordered:
        if cart_item.cart.applied_coupon_type:
            # Check if other items in the cart still have the same coupon
            items_with_coupon = CartItem.objects.filter(cart=cart_item.cart, item__name=cart_item.item.name).exclude(id=cart_item.id)

            if items_with_coupon.exists():
                # If other items have the same coupon, do not remove it
                cart_item.delete()
            else:
                # Remove the coupon if no other items have it
                cart_item.cart.discount = 0
                cart_item.cart.applied_coupon_type = None
                cart_item.cart.save()
                cart_item.delete()
        else:
            cart_item.delete()

    return redirect('cart')

@login_required
def empty_cart(request):
    carts = Cart.objects.filter(user=request.user, ordered=0)
    print("carts")
    for cart in carts:
        if not cart.ordered:
            cart.delete()
    
    return redirect('cart')

@login_required
def add_to_cart_from_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    extras_str = request.POST.get('extras', '')
    extras = [int(extra_id) for extra_id in extras_str.split(',') if extra_id.isdigit()]
    print(extras)
    cart, created = Cart.objects.get_or_create(user=request.user, is_delivered=0)
    if not created and not cart.ordered:

        try:
            cart_items = CartItem.objects.annotate(num_extras=Count('extras')).filter(
                cart=cart,
                item=item,
            ).filter(num_extras=len(extras)).distinct()
            for cart_item in cart_items:
                if set(cart_item.extras.values_list('id', flat=True)) == set(extras):      
                    cart_item.quantity += 1
                    try:
                        coupon = Coupons.objects.get(id=cart_item.cart.discount)
                        if cart_item.cart.applied_coupon_type == 'percentage' and coupon.product == item.name:
                            print("couponed item adding")
                            #print(item.price, cart_item.get_extras_price(), cart_item.quantity, coupon.percentage)
                            cart_item.final_price = (item.price + cart_item.get_extras_price()) * cart_item.quantity * (1 - coupon.percentage  / 100)
                        else:
                            cart_item.final_price = (item.price + cart_item.get_extras_price() ) * cart_item.quantity
                        cart_item.save()
                    except Coupons.DoesNotExist:
                        print("no coupon")
                        cart_item.final_price = (item.price + cart_item.get_extras_price() ) * cart_item.quantity
                        cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, item=item, quantity=1, final_price=item.price, total_price=item.price)
    calculate_total_price(cart)
    
    return redirect('cart')

@login_required  
def order(request, id):
    cart = Cart.objects.get(pk = id)
    if cart.user_id == request.user.id:
        calculate_total_price(cart)
        cart.ordered = 1
        cart.order_time = datetime.now(pytz.timezone('Europe/Budapest'))
        cart.save()
        Qr_code_reads.objects.filter(user=request.user, ordered=0).update(ordered=1)
    else:
        print("not authorized")
        messages.error(request, 'You are not authorized to order this cart.')
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
                        extras = item.get_extras_price()
                        item.total_price -= (percentage_discount * (item.total_price) / 100)
                        item.final_price = (item.total_price + extras) * item.quantity
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


def handle_cart_item(cart, item, comment="", extras=[]):
    existing_cart_items = CartItem.objects.filter(cart=cart, item=item, comment=comment)
    print('extras', extras)
    print('existing_cart_item', existing_cart_items)
    # Check if there are any existing cart items with the same extras
    for existing_cart_item in existing_cart_items:
        
        if extras:
            existing_extras = set(existing_cart_item.extras.all())
            new_extras = set(extras)

            new_item_extras = set()

            for extra in new_extras:
                new_item_extras.update(Extra.objects.filter(id=extra))
                print('new_extras', new_extras)
                print('existing_extras', existing_extras)

                if existing_extras == new_item_extras:
                    print('same extras')
                    # If extras are the same, increase the quantity and save
                    existing_cart_item.quantity += 1
                    existing_cart_item.final_price = (item.price) * existing_cart_item.quantity
                    existing_cart_item.total_price = item.price
                    existing_cart_item.save()
                    return existing_cart_item.quantity


        if extras == None and Menuitem.objects.get(id=existing_cart_item.item.id).type == 0:
            print('ital')
            existing_cart_item.quantity += 1
            existing_cart_item.final_price = (existing_cart_item.total_price) * existing_cart_item.quantity
            existing_cart_item.save()
            existing_cart_item.cart.save()
            return existing_cart_item.quantity
        

    # If no matching cart items are found, create a new one
    if cart.discount:
        discount = Coupons.objects.get(id=cart.discount)
        if discount.coupon_type == 'percentage':
            print("percentage")
            cart_item = CartItem.objects.create(
                cart=cart,
                item=item,
                quantity=1,
                final_price=item.price * (1 - discount.percentage / 100),
                total_price=item.price * (1 - discount.percentage / 100),
                comment=comment
            )
            if extras:
                cart_item.extras.set(extras)
            cart_item.final_price = (cart_item.total_price + cart_item.get_extras_price()) * cart_item.quantity #sorrend fontos mert a total price a final price-bol szamolodik
            cart_item.total_price = cart_item.total_price + cart_item.get_extras_price()

            cart_item.save()


    else:
        cart_item = CartItem.objects.create(
            cart=cart,
            item=item,
            quantity=1,
            final_price=item.price,
            total_price=item.price,
            comment=comment
        )
        if extras:
            cart_item.extras.set(extras)
        cart_item.final_price = (cart_item.total_price + cart_item.get_extras_price()) * cart_item.quantity
        cart_item.total_price = cart_item.total_price
        cart_item.save()

    return cart_item.quantity

def get_extras(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    #extras = item.extras.all()
    print(item.category)
    extras = Extra.objects.filter(category=item.category)
    data = [{'id': extra.id, 'name': extra.name, 'price': extra.price} for extra in extras]
    print(data)
    return JsonResponse(data, safe=False)

def calculate_total_price(cart):
    total_price = 0

    for cart_item in CartItem.objects.filter(cart=cart):
        total_price += cart_item.final_price + cart_item.get_extras_price()
        cart_item.save()
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

            # Calculate total price for eligible item with extras
            eligible_item_total_price = 0
            cart_items = CartItem.objects.filter(cart=cart, item=eligible_item)

            for cart_item in cart_items:
                eligible_item_total_price += cart_item.final_price + cart_item.get_extras_price()

            # Adjust the discount calculation to consider the total price with extras
            discount = eligible_item_total_price * percentage_coupon.percentage / 100

    return discount


