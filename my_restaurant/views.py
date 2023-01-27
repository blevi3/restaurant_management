# djangotemplates/example/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView # Import TemplateView
from .forms import NewUserForm, NewItemForm
from django.contrib.auth import login
from django.contrib import messages
import sqlite3
from .models import Menuitem
from django.shortcuts import get_object_or_404

# Add the two views we have been talking about  all this time :)
class HomePageView(TemplateView):
    template_name = "index.html"


class AboutPageView(TemplateView):
    template_name = "about.html"


def getdata(request):

    print(id)
    files = []
    if request.method == "POST":
        print("posted")
        newitem = NewItemForm(request.POST)
        if newitem.is_valid(): 
            print("valid")
            item = newitem.save(commit=False)
            item.save()

    item_list = Menuitem.objects.all()
    return render(request, 'data.html', {'files': item_list})


def modifydata(request,id):
    print("hello")

    if request.method == 'POST':
        obj = Menuitem.objects.get(pk=id)

        data = NewItemForm(request.POST, instance=obj)
        if data.is_valid():
            data.save()
            return redirect(to='users-profile')
    else:
        data = NewItemForm(instance=obj)
    return render(request, 'data.html', {"olddata": data})


def items_list(request):
    item_list = Menuitem.objects.all()
    print("fsaf")
    if request.method == 'POST':
        if 'edit' in request.POST:
            item = get_object_or_404(Menuitem, pk=request.POST['edit'])
            item.name = request.POST.get('add')
            item.price = request.POST.get('price')
            print(item.category)
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
			return redirect("/accounts/login")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="registration/register.html", context={"register_form":form})
    
