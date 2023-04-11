# djangotemplates/example/views.py
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView # Import TemplateView
from .forms import NewUserForm, NewItemForm, ReservationForm, DateSelectionForm, ProfileForm
from django.contrib.auth import login
from django.contrib import messages
import sqlite3
from .models import Menuitem, Cart, CartItem, Table, Reservation, Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta, date
from django.utils import timezone

from django.contrib.auth.decorators import user_passes_test


from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

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





import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
@login_required
def payment(request):
    if request.method == 'POST':
        amount = 1000 # amount in cents
        email = request.POST['email']
        token = request.POST['stripeToken']
        try:
            customer = stripe.Customer.create(
                email=email,
                source=token
            )
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                customer=customer.id,
                description='Example charge'
            )
            # do something after successful payment
            return render(request, 'payment_success.html')
        except stripe.error.CardError as e:
            # handle errors
            pass
    context = {
        'publishable_key': settings.STRIPE_TEST_PUBLISHABLE_KEY
    }
    return render(request, 'payment.html', context)

def payment_success(request):
    return render(request, 'payment_success.html')





from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from .models import Profile

@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
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
    }
    return render(request, 'profile.html', context)


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "registration/password_reset_email.html"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'g.laszlo2003@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="registration/password_reset.html", context={"password_reset_form":password_reset_form})


@staff_member_required
def all_reservations(request):
    reservations = Reservation.objects.filter(end_time__gt=timezone.now()).order_by('start_time')
    return render(request, 'all_reservations.html', {'reservations': reservations})


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

'''
@login_required
def date_selection(request):
    
    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            date1 = form.cleaned_data['date']
            return redirect('available_tables', date=date1)
    else:
        form = DateSelectionForm()
    return render(request, 'date_selection.html', {'form': form})


@login_required
def available_tables(request):
    date_str = request.POST.get('date')
    
    if date_str:
        date1 = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date1 = date.today()
    
    tables = Table.objects.all()
    reserved = {}
    for table in tables:
        reserv = Reservation.objects.all().filter(table_id = table.id)
        
        reserved[table.id] = reserv
    print(reserved)

    return render(request, 'available_tables.html', {'tables': tables,  'date': date1, })
'''

from django.core.exceptions import ValidationError
from datetime import timedelta

@login_required
def available_tables(request):
    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            # populate form with selected date
            form = DateSelectionForm(initial={'date': date})
            # check selected date is not too far in the future
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
        reserved = {}
        for table in tables:
            reserv = Reservation.objects.all().filter(table_id=table.id)

            reserved[table.id] = reserv

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
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.table = table
            start_time_str = request.POST.get('starttime')
            end_time_str = request.POST.get('endtime')
            party_size = request.POST.get('party_size')
            print(party_size)
            print(table.max_capacity)
            try:
            
            # Validate the party size
                if int(party_size) > table.max_capacity:
                    raise ValidationError(f"Party size cannot exceed {table.max_capacity}.")
                starter = date1+" "+start_time_str
                ender = date1+" "+end_time_str
                print(starter)
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
                return render(request, 'reservation_table.html', {'table': table, 'error_message': cleaned_message,  'form': form, 'date1': date1, 'reserved_time': reserved_times_values})
    else:
        form = ReservationForm()
    print(reserved_times_values)
        

    return render(request, 'reservation_table.html', {'table': table,  'form': form, 'date1': date1, 'reserved_time': reserved_times_values})

def drinks(request):
    drinks = Menuitem.objects.all().filter(type = 0)  
    categories = []
    for categorie in drinks:
        categories.append(categorie.category)
    print(categories)
    cat = list(set(categories))
    print(cat)
    return render(request, 'drinks.html', {'drinks': drinks, 'categories':cat})

def menu(request):
    foods = Menuitem.objects.all().filter(type = 1)
    categories = []
    for food in foods:
        categories.append(food.category)
    cat = list(set(categories))
    print(categories)


    return render(request, 'foods.html', {'foods': foods, 'categories': cat})


@login_required()
def add_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    print(item)
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    if not created:
        cart.save()
    if not cart.ordered:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.final_price = item.price * cart_item.quantity
            cart_item.save()
            print(cart_item.quantity)
            print("növelve")
        else:
            print("setto 1")
            cart_item.quantity = 1
            cart_item.total_price = item.price * cart_item.quantity
            cart_item.final_price = item.price
            cart_item.save()
    
    return redirect('order')
@login_required
def cart(request):
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    cart_items = {}
    final_price = 0
    if not created:
        cart_items = CartItem.objects.filter(cart=cart)
        final_price = 0
        for cart_item in cart_items:
            final_price+=cart_item.quantity*cart_item.total_price
        cart.amount_to_be_paid = final_price
        cart.save()
    context = {
        'final_price': final_price*100,  # assuming you have this variable in your view
        'publishable_key': settings.STRIPE_TEST_PUBLISHABLE_KEY,  # replace with your actual publishable key
    }
    return render(request, 'cart.html', {'cart_items': cart_items, 'final_price': final_price, 'ordered': cart.ordered, 'cartid': cart.id,'publishable_key': settings.STRIPE_TEST_PUBLISHABLE_KEY})
@login_required
def previous_orders(request):
    previous_carts= Cart.objects.filter(ordered=1).filter(is_delivered = 1).filter(user = request.user)
    print(previous_carts)
    return render(request, 'previous_orders.html', {'previous_carts': previous_carts})
@login_required
def remove_from_cart(request, cart_item_id):
    print(cart_item_id)
    
    cart_item = CartItem.objects.get(id=cart_item_id)
    item = Menuitem.objects.get(id = cart_item.item_id)
    cart_item.total_price = item.price
    cart = Cart.objects.filter(id = cart_item.cart_id ,ordered=0)
    if cart:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.final_price = cart_item.total_price * cart_item.quantity
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
        print(cart_item.quantity)
    return redirect('cart')

@staff_member_required
def all_orders(request):
    paid_carts = Cart.objects.filter(is_paid=True, is_delivered=False)
    unpaid_carts = Cart.objects.filter(is_paid=False, is_delivered=False)
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
        
        print(categories)

        if 'edit' in request.POST:
            print("edit")
            item = get_object_or_404(Menuitem, pk=request.POST['editItemID'])
            item.name = request.POST.get('edit')
            item.price = request.POST.get('price')
    
            item.save()
        elif 'remove' in request.POST:
            print("remove")
            item = get_object_or_404(Menuitem, pk=request.POST['remove'])
            print("remove")
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
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            profile = Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form":form})





class Testpage(TemplateView):
    template_name = "index.html"
