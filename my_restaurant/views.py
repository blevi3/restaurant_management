# djangotemplates/example/views.py
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView # Import TemplateView
from .forms import NewUserForm, NewItemForm
from django.contrib.auth import login
from django.contrib import messages
import sqlite3
from .models import Menuitem, Cart, CartItem
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required()
def add_to_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    print(item)
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    if not created:
        cart.save()
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
    cart_item = CartItem.objects.get(id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect(reverse('cart'))

def add_to_cart_from_cart(request, item_id):
    item = get_object_or_404(Menuitem, pk=item_id)
    cart, created = Cart.objects.filter(is_delivered = 0).get_or_create(user=request.user)
    if not created:
        cart.save()
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
    
        if 'edit' in request.POST:
            print("edit")
            item = get_object_or_404(Menuitem, pk=request.POST['editItemID'])
            item.name = request.POST.get('edit')
            item.price = request.POST.get('price')
    
            item.save()
        elif 'remove' in request.POST:
            item = get_object_or_404(Menuitem, pk=request.POST['remove'])
            print("remove")
            item.delete()
        elif 'add' in request.POST:
            if request.POST.get('type') == "Food":
                newtype = 0
            else:
                newtype = 1
            Menuitem.objects.create(
                name=request.POST.get('add'),
                price=request.POST.get('price'),
                type = newtype,
                category = request.POST.get('category')
            )
    return render(request, 'data.html', {'item_list': item_list})


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
    
