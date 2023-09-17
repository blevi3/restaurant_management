from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Cart


@login_required
def previous_orders(request):
    previous_carts= Cart.objects.filter(ordered=1).filter(is_delivered = 1).filter(user = request.user)
    return render(request, 'previous_orders.html', {'previous_carts': previous_carts})



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

