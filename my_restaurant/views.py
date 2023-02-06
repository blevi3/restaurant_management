# djangotemplates/example/views.py
from django.shortcuts import render, redirect
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
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not created:
        cart.save()
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        print(cart_item.quantity)
        print("növelve")
    else:
        print("setto 1")
        cart_item.quantity = 1
        cart_item.total_price = item.price * cart_item.quantity
        cart_item.save()
    return redirect('data')



def item_list(request):
    items = Menuitem.objects.all()
    return render(request, 'item_list.html', {'items': items})

def cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, 'cart.html', {'cart_items': cart_items})



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
    
