# djangotemplates/example/views.py
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView # Import TemplateView
from .forms import NewUserForm, NewItemForm, ReservationForm, DateSelectionForm
from django.contrib.auth import login
from django.contrib import messages
import sqlite3
from .models import Menuitem, Cart, CartItem, Table, Reservation
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta, date
from django.utils import timezone

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
    '''reserved_tables = Reservation.objects.filter(start_time__date=date1).values_list('table_id', flat=True)
    available_tables = tables.exclude(id__in=reserved_tables)
    print(available_tables)
    table_times = {}
    for table in available_tables:
        
        reserved_times = Reservation.objects.filter(table=table, start_time__date=date1).order_by('start_time').values_list('start_time', 'end_time')
        available_times = get_available_times(date1, table)
        table_times[table.id] = available_times'''
    
    reserved = {}
    for table in tables:
        reserv = Reservation.objects.all().filter(table_id = table.id)
        
        reserved[table.id] = reserv
    print(reserved)

    return render(request, 'available_tables.html', {'tables': tables,  'date': date1, })


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
    return render(request, 'drinks.html', {'drinks': drinks})

def menu(request):
    foods = Menuitem.objects.all().filter(type = 1)
    return render(request, 'foods.html', {'foods': foods})


 



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
    
    return redirect('data')

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
    return render(request, 'cart.html', {'cart_items': cart_items, 'final_price': final_price, 'ordered': cart.ordered, 'cartid': cart.id})


def previous_orders(request):
    previous_carts= Cart.objects.filter(ordered=1).filter(is_delivered = 1).filter(user = request.user)
    print(previous_carts)
    return render(request, 'previous_orders.html', {'previous_carts': previous_carts})

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


def trash_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart = Cart.objects.filter(id = cart_item.cart_id ,ordered=0)
    if cart:
        cart_item.delete()
    return redirect(reverse('cart'))

def empty_cart(request):

    cart = Cart.objects.filter(user = request.user ,ordered=0)
    if cart:
        cart.delete()
    return redirect(reverse('cart'))


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

def all_orders(request):
    
    ordered_carts= Cart.objects.filter(ordered=1).filter(is_delivered = 0)
    return render(request, 'all_orders.html', {'carts': ordered_carts})

def cart_paid(request, id):
    cart = Cart.objects.get(pk = id)
    cart.is_delivered = 1
    cart.save()
    return redirect('all_orders')
    
def order(request, id):
    cart = Cart.objects.get(pk = id)
    cart.ordered = 1
    cart.save()
    return redirect('cart')
    
    
# Add the two views we have been talking about  all this time :)
class HomePageView(TemplateView):
    template_name = "index.html"


class AboutPageView(TemplateView):
    template_name = "about.html"

class test(TemplateView):
    template_name = "home.html"


def items_list(request):
    item_list = Menuitem.objects.all()
    if request.method == 'POST':
        categories = item_list.values_list('category', flat=True).distinct()
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
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="registration/register.html", context={"register_form":form})
    
