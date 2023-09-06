from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView # Import TemplateView
from .forms import NewUserForm, NewItemForm, ReservationForm, DateSelectionForm, ProfileForm , CouponForm, CreateCouponForm
from django.contrib.auth import login
from django.contrib import messages
import sqlite3
from .models import Menuitem, Cart, CartItem, Reservation, Profile , Coupons, Table
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta, date
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.decorators import user_passes_test


from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
import stripe
from decimal import Decimal
from reportlab.lib.pagesizes import letter
import io
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def staff_member_required(view_func):
    """
    Decorator that checks if a user is a staff member or not. If not, redirect to login page.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/accounts/login/',
        redirect_field_name='next'
    )
    return actual_decorator(view_func)

from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from .models import Profile



@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid() :
            user_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
    context = {
        'user_form': user_form,
        'points': Profile.objects.get(user=request.user).points
    }
    return render(request, 'profile.html', context)

def delete_account(request):
    if request.method == 'POST':
        # Delete the user's account
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')  # Replace 'home' with the URL name for your home page
    return redirect('profile')

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(email=data)              

            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.html"
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            "g.laszlo2003@gmail.com",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="registration/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )

@staff_member_required
def all_reservations(request):
    reservations = Reservation.objects.filter(end_time__gt=timezone.now()).order_by('start_time')
    past_reservations = Reservation.objects.exclude(id__in=reservations.values_list('id', flat=True))

    return render(request, 'all_reservations.html', {'reservations': reservations, "past_reservations": past_reservations})

@login_required
def my_reservations(request):
    now = timezone.now()
    reservations = Reservation.objects.filter(user=request.user)
    current_reservations = sorted(reservations.filter(start_time__gte=now), key=lambda r: r.start_time)
    past_reservations = sorted(reservations.filter(end_time__lt=now), key=lambda r: r.start_time, reverse=True)
    context = {
        'reservations': reservations,
        'now': now,
        'current_reservations': current_reservations,
        'past_reservations': past_reservations
    }
    return render(request, 'my_reservations.html', context)

from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Table  

@login_required
def available_tables(request):
    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            form = DateSelectionForm(initial={'date': date})
            max_future_days = 60
            if date > date.today() + timedelta(days=max_future_days):
                raise ValidationError('Selected date is too far in the future')
        else:
            date = None
    else:
        form = DateSelectionForm()
        date = None

    if date:
        tables = Table.objects.all()


        return render(request, 'reservation.html', {'tables': tables, 'date': date, 'form': form})
    else:
        return render(request, 'reservation.html', {'form': form})

@login_required
def get_available_times(date1, table):
    
    reserved_times = Reservation.objects.filter(start_time__date=date1, table=table).order_by('start_time')
    reserved_times_list = list(reserved_times.values_list('start_time', 'end_time'))

    # Create a list of all the possible time slots
    time_slots = []
    
    start_time = datetime.combine(date1, time(9, 0))  # Start time for reservations
    end_time = datetime.combine(date1, time(23, 0))  # End time for reservations
    while start_time < end_time:
        time_slots.append((start_time.time(), (start_time + timedelta(minutes=30)).time()))
        start_time += timedelta(minutes=30)

    # Remove any time slots that are already reserved
    available_times = []
    for time_slot in time_slots:
        if time_slot not in reserved_times_list:
            available_times.append(time_slot)

    return available_times

@login_required
def reservation_table(request, table_id, date1):
    table = get_object_or_404(Table, id=table_id)
    reserved_times = Reservation.objects.all().filter(table_id = table_id).filter(start_time__contains=date1)
    reserved_times_values = []
    for i in range(len(reserved_times)):
        reserved_times_values.append({'start_time': reserved_times[i].start_time.strftime("%Y-%m-%d %H:%M"), 'end_time': reserved_times[i].end_time.strftime("%Y-%m-%d %H:%M")})
    #date1 = request.POST.get('date')
    #available_times = get_available_times(date1, table)
    
    if date1 == datetime.now().strftime("%Y-%m-%d"):  # Check if date1 is today
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day, 8, 0)  # 08:00 AM

        past_times_values2 = []
        time_increment = timedelta(minutes=15)
        current_time = start_of_day
        while current_time < now:
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M")
            past_times_values2.append({
                'start_time': formatted_time,
                'end_time': (current_time + time_increment).strftime("%Y-%m-%d %H:%M")
            })
            current_time += time_increment

        reserved_times_values2 = past_times_values2 + reserved_times_values  # Combine past and reserved times
    else:
        reserved_times_values2 = reserved_times_values

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.table = table
            start_time_str = request.POST.get('starttime')
            end_time_str = request.POST.get('endtime')
            party_size = request.POST.get('party_size')
            try:
            
            # Validate the party size
                if int(party_size) > table.max_capacity:
                    raise ValidationError(f"Party size cannot exceed {table.max_capacity}.")
                starter = date1+" "+start_time_str
                ender = date1+" "+end_time_str
                start_time = datetime.strptime(starter, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(ender, '%Y-%m-%d %H:%M:%S')
                reservation.start_time = start_time
                reservation.end_time = end_time
                reservation.save()
                messages.success(request, 'Reservation successful!')
                return redirect('home')
            
            except ValidationError as e:
            # Display the error message on the screen
                error_message = str(e)
                cleaned_message = error_message[2:-2]
                return render(request, 'reservation_table.html', {'table': table, 'error_message': cleaned_message,  'form': form, 'date1': date1, 'reserved_time': reserved_times_values, "past_times": reserved_times_values2})
    else:
        form = ReservationForm()
        

    return render(request, 'reservation_table.html', {'table': table,  'form': form, 'date1': date1, 'reserved_time': reserved_times_values, "past_times": reserved_times_values2})

def drinks(request):
    drinks = Menuitem.objects.all().filter(type = 0)  
    categories = []
    for categorie in drinks:
        categories.append(categorie.category)
    cat = list(set(categories))
    

    foods = Menuitem.objects.all().filter(type = 1)
    categories2 = []
    for food in foods:
        categories2.append(food.category)
    cat2 = list(set(categories2))
    
    return render(request, 'drinks.html', {'drinks': drinks, 'categories':cat, 'foods': foods, 'categories2': cat2})

def menu(request):
    foods = Menuitem.objects.all().filter(type = 1)
    categories = []
    for food in foods:
        categories.append(food.category)
    cat = list(set(categories))

    return render(request, 'foods.html', {'foods': foods, 'categories': cat})

def gallery(request):
    return render(request, 'gallery.html' )

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


@staff_member_required
def create_coupon(request):
    coupons = Coupons.objects.all()  # Retrieve all coupons

    if request.method == 'POST':
        form = CreateCouponForm(request.POST)

        if form.is_valid():
            coupon_type = form.cleaned_data['coupon_type']
            code = form.cleaned_data['code']
            product = form.cleaned_data['product']
            is_unique = form.cleaned_data['is_unique']

            # Initialize coupon object based on the selected coupon type
            if coupon_type == 'fixed':
                fixed_amount = form.cleaned_data['percentage']
                coupon = Coupons(
                    coupon_type=coupon_type,
                    fixed_amount=fixed_amount,
                    code=code,
                    product=product if coupon_type == 'percentage' else None,
                    is_unique=is_unique
                )
            elif coupon_type == 'percentage':
                percentage = form.cleaned_data['percentage']
                coupon = Coupons(
                    coupon_type=coupon_type,
                    percentage=percentage,
                    code=code,
                    product=product,
                    is_unique=is_unique
                )
            else:
                # Handle any other coupon types if needed
                pass

            coupon.save()
            return redirect('create_coupon')  # Redirect to the coupon list page after creation

    else:
        # Display the form for creating a new coupon
        form = CreateCouponForm()

    return render(request, 'create_coupon.html', {'form': form, 'coupons': coupons})

@staff_member_required
def remove_coupon(request, coupon_id):
    if request.method == 'POST':
        try:
            coupon = Coupons.objects.get(pk=coupon_id)
            coupon.delete()
        except Coupons.DoesNotExist:
            pass 
    return redirect('create_coupon') 

@login_required
def remove_coupon_from_cart(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user, ordered=False)
        if cart.discount != 0:
            # Get the coupon code and associated discount
            removed_coupon = Coupons.objects.get(id=cart.discount)
            cart.discount = 0

            # Revert the prices of items that were discounted by the coupon
            cart_items = CartItem.objects.filter(cart=cart)
            print("cart items",cart_items)
            if removed_coupon.coupon_type == 'fixed':
                print("fixed")
                # Revert fixed amount coupon
                cart.amount_to_be_paid += removed_coupon.fixed_amount
                cart.reduced_price = 0
                cart.applied_coupon_type = None
                cart.save()

            elif removed_coupon.coupon_type == 'percentage':
                for cart_item in cart_items:
                    if cart_item.item.id == Menuitem.objects.get(name = removed_coupon.product).id:
                        # Retrieve the original price from the Menuitem model
                        original_price = Menuitem.objects.get(id=cart_item.item.id).price
                        print("oroginal proce",original_price)

                        # Update the CartItem's total_price with the original price
                        cart_item.total_price = original_price
                        cart.applied_coupon_type = None

                        cart_item.save()

                cart.save()
                messages.success(request, 'Coupon removed successfully.')
        else:
            messages.warning(request, 'No coupon to remove.')

    return redirect('cart')  # Redirect back to the cart page


@login_required
def previous_orders(request):
    previous_carts= Cart.objects.filter(ordered=1).filter(is_delivered = 1).filter(user = request.user)
    return render(request, 'previous_orders.html', {'previous_carts': previous_carts})
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

@staff_member_required
def all_orders(request):
    paid_carts = Cart.objects.filter(is_paid=True, is_delivered=False, ordered = True)
    unpaid_carts = Cart.objects.filter(is_paid=False, is_delivered=False, ordered = True)
    return render(request, 'all_orders.html', {'paid_carts': paid_carts, 'unpaid_carts': unpaid_carts})
def order_paid_admin(request, id):
    cart = Cart.objects.get(pk = id)
    cart.ordered = 1
    cart.is_paid = 1
    cart.save()
    return redirect('all_orders')

@staff_member_required
def cart_delivered(request, id):
    cart = Cart.objects.get(pk = id)

    cart.is_delivered = 1
    cart.save()
    return redirect('all_orders')
@login_required  
def order(request, id):
    cart = Cart.objects.get(pk = id)
    cart.ordered = 1
    cart.save()
    return redirect('cart')
    
def order_paid(request, id):
    cart = Cart.objects.get(pk = id)
    cart.ordered = 1
    cart.is_paid = 1
    cart.save()
    return redirect('cart') 

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


class HomePageView(TemplateView):
    template_name = "index.html"


class AboutPageView(TemplateView):
    template_name = "about.html"

class home(TemplateView):
    template_name = "home.html"


def items_list(request):
    
    item_list = Menuitem.objects.all()
    categories = item_list.values_list('category', flat=True).distinct()
    if request.method == 'POST':
        

        if 'edit' in request.POST:
            item = get_object_or_404(Menuitem, pk=request.POST['editItemID'])
            item.name = request.POST.get('edit')
            item.price = request.POST.get('price')
    
            item.save()
        elif 'remove' in request.POST:
            item = get_object_or_404(Menuitem, pk=request.POST['remove'])
            item.delete()
        elif 'add' in request.POST:
            if request.POST.get('type') == "Food":
                newtype = 1
            else:
                newtype = 0
            Menuitem.objects.create(
                name=request.POST.get('add'),
                price=request.POST.get('price'),
                type = newtype,
                category = request.POST.get('category')
            )
            
    return render(request, 'data.html', {'item_list': item_list, 'categories': categories})

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if not User.objects.filter(username=request.POST.get("username")).exists():
            if not User.objects.filter(email=request.POST.get("email")).exists():
                if form.is_valid():
                    username = form.cleaned_data.get('username')
                    email = form.cleaned_data.get('email')
        
                    user = form.save()
                    messages.success(request, f'Account created for {username}!')
                    
                    # Check if a Profile already exists for the user
                    profile, created = Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'username': username,
                            'email': email,
                        }
                    )
                    if not created:
                        # Update the existing profile
                        profile.username = username
                        profile.email = email
                        profile.save()
                    
                    login(request, user)
                    messages.success(request, "Registration successful.")
                    return redirect("home")
                else:
                    messages.error(request, "Password and confirm password do not match.")
                    return render(request, 'registration/register.html', {'register_form': form, 'uname': request.POST.get("username"), 'address': request.POST.get("email")})
            else:
                messages.error(request, "Email address already registered")
                return render(request, 'registration/register.html', {'register_form': form, 'uname': request.POST.get("username")})
        else:
            messages.error(request, "The username is occupied")
            return render(request, 'registration/register.html', {'register_form': form, 'address': request.POST.get("email")})
    else:
        form = NewUserForm()
    return render(request, template_name="registration/register.html", context={"register_form": form})



def get_recommendations(cart_items, num_recommendations=3):
    from collections import Counter
    from itertools import groupby

    order_history = CartItem.objects.all().values_list('cart_id', 'item_id')

    product_pairs = Counter()
    for cart_id, items in groupby(order_history, key=lambda x: x[0]):
        ordered_items = set(items)
        for item1 in ordered_items:
            for item2 in ordered_items:
                if item1 != item2:
                    product_pairs[(item1[1], item2[1])] += 1

    cart_products = cart_items
    recommendations = []
    for product_pair, frequency in product_pairs.items():
        if product_pair[0] in cart_products and product_pair[1] not in cart_products:
            recommendations.append((product_pair[1], frequency))
        elif product_pair[1] in cart_products and product_pair[0] not in cart_products:
            recommendations.append((product_pair[0], frequency))
    recommendations.sort(key=lambda x: x[1], reverse=True)
    unique_recommendations = list(set(recommendations))
    unique_recommendations.sort(key=lambda x: x[1], reverse=True)
    unique_product_ids = [product_id for product_id, _ in unique_recommendations]
    recom = list(set(unique_product_ids))[:num_recommendations]
    return recom


class Testpage(TemplateView):
    template_name = "index.html"


def get_user_cart_items(user):
    # Retrieve the cart for the user
    cart = Cart.objects.filter(user_id=user.id, ordered=0, is_delivered=0, is_paid=0, is_ready=0).first()

    if cart:
        cart_items = CartItem.objects.filter(cart_id=cart.id)
        line_items2 = []

        for cart_item in cart_items:
            menu_item = Menuitem.objects.get(id=cart_item.item_id)
            line_item2=[int(cart_item.total_price), menu_item.name, cart_item.quantity]
            line_items2.append(line_item2)

        return line_items2, cart
    else:
        return []

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_TEST_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        try:
            user_items, cart= get_user_cart_items(request.user)
            line_items = []
            for item in user_items:
                line_item = {
                    'price_data': {
                        'currency': 'huf',
                        'unit_amount': item[0]*100,  
                        'product_data': {
                            'name': item[1],    
                        },
                    },
                    'quantity': item[2],  
                }
                line_items.append(line_item)

            discount = 0
            if cart.applied_coupon_type == 'fixed':
                discount = Coupons.objects.filter(id=cart.discount).first().fixed_amount
                print("discount: ",discount)
            
                coupon = stripe.Coupon.create(
                        percent_off=None,
                        amount_off=int(discount)*100,  # The discount value in cents (-500ft)
                        currency="huf",
                        duration="once",  # Adjust duration as needed
                    )


                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url + 'cart',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='payment',
                    
                    line_items=line_items,
                    discounts=[{
                        'coupon': coupon.id,
                    }],
                )

            else:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url + 'cart',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=line_items,
                )


            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class SuccessView(TemplateView):
    template_name = 'payment_success.html'


class CancelledView(TemplateView):
    template_name = 'payment_cancelled.html'


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['client_reference_id']
        print("user id: ",user_id)
        user = User.objects.get(id=user_id)
        cart = Cart.objects.filter(user=user, ordered=0, is_delivered=0, is_paid=0, is_ready=0).first()

        if cart:
            if cart.discount !=0:
                used_coupon = Coupons.objects.filter(id=cart.discount).first()
                if used_coupon.is_unique == 1:
                    used_coupon.delete()
            cart.ordered = 1
            cart.is_paid = 1
            cart.discount = 0
            cart.applied_coupon_type = None
            cart.reduced_price = 0
            cart.save()
            print("cart: ",cart)
            
            
        print("Payment was successful. Cart updated.")
        user_items = CartItem.objects.filter(cart_id=cart.id)
        subtotal = 0
        for item in user_items:
            total_item_price = item.item.price * item.quantity
            subtotal += total_item_price
        user = Profile.objects.get(id=user_id)
        user.points += subtotal/100
        user.save()
        pdf_response = generate_pdf_receipt(cart.id, user_items, user, session['payment_intent'])

        # Send the PDF receipt via email using send_mail
        send_email_with_pdf(cart.id, pdf_response, user.email)
        print("PDF receipt sent via email.")
  


    return HttpResponse(status=200)

def generate_pdf_receipt(order_id, items, user, transaction_number):
    # Create a PDF in memory
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles for the document
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Title
    title = Paragraph("Order Receipt", styles['Heading1'])
    elements.append(title)

    # Pub Information
    pub_info = [
        ("Legenda Pub",),
        ("Address: 123 Main Street, Cityville",),
        ("Phone: +1 (123) 456-7890",),
    ]
    for info in pub_info:
        elements.append(Paragraph(info[0], normal_style))
        elements.append(Spacer(1, 12))  # Add a small gap after each piece of information

    # Transaction Details
    transaction = [
        ("Transaction Number:", transaction_number),
        ("Date:", timezone.now().strftime('%Y-%m-%d %H:%M:%S')),
        ("Cashier:", "John Doe"),
        ("Payment Method:", "Credit Card"),
    ]
    transaction_table = Table(transaction)
    transaction_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('SIZE', (0, 0), (-1, -1), 12),
    ]))
    elements.append(transaction_table)

    # Customer Information
    customer_info = [
        ("Customer Name:", user.username),
        ("Email:", user.email),
    ]
    customer_info_table = Table(customer_info)
    customer_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('SIZE', (0, 0), (-1, -1), 12),
    ]))
    elements.append(customer_info_table)

    # Add a gap before the ordered items table
    elements.append(Spacer(1, 24))

    # Order Details
    data = [["Item", "Quantity", "Price", "Total"]]
    subtotal = 0
    for item in items:
        total_item_price = item.item.price * item.quantity
        data.append([item.item.name, item.quantity, f"{item.item.price} HUF", f"{total_item_price} HUF"])
        subtotal += total_item_price

    subtotal = 0.73 * subtotal 
    # Calculate VAT (27%)
    vat = 0.27 * subtotal

    table = Table(data)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), '#333333'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#EEEEEE'),
        ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC')
    ]))
    elements.append(table)

    # Totals
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Subtotal: {subtotal} HUF", normal_style))
    elements.append(Paragraph(f"VAT (27%): {vat:.2f} HUF", normal_style))
    total = subtotal + vat
    elements.append(Paragraph(f"Total: {total} HUF", normal_style))

    # Thank You Message
    thank_you_message = "Thank you for your purchase!"
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(thank_you_message, normal_style))

    doc.build(elements)

    # Rewind the buffer to the beginning
    buffer.seek(0)

    return buffer


def send_email_with_pdf(order_id, pdf_buffer, recipient_email):
    subject = 'Your Receipt'
    message = 'Thank you for your order. Here is your receipt.'
    from_email = 'your_email@example.com'  # Replace with your email address
    to_email = [recipient_email]

    email = EmailMessage(subject, message, from_email, to_email)
    email.attach(f'receipt_{order_id}.pdf', pdf_buffer.read(), 'application/pdf')  # Use pdf_buffer.read()

    # Send the email using send_mail
    email.send(fail_silently=False)