# djangotemplates/example/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView # Import TemplateView
from .forms import NewUserForm, NewItemForm
from django.contrib.auth import login
from django.contrib import messages
import sqlite3
from .models import Menuitem

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



    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    for row in cur.execute("SELECT * FROM my_restaurant_menuitem"+";"):
        files0 = row[0]
        files1 = row[1]
        files2 = row[2]
        files3 = row[3]
        files4 = row[4]
        files = cur.fetchall()

    filedictlist = []

    filedict0 = {}
    filedict0['id'] = files0
    filedict0['name'] = files1
    filedict0['category'] = files2
    filedict0['type'] = files3
    filedict0['price'] = files4
    filedictlist.append(filedict0)

    for i in range(len(files)):
        filedict = {}
        filedict['id'] = files[i][0]
        filedict['name'] = files[i][1]
        filedict['category'] = files[i][2]
        filedict['type'] = files[i][3]
        filedict['price'] = files[i][4]
        print(files[i][0])
        filedictlist.append(filedict)
   

    return render(request, 'data.html', {"files": filedictlist})

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
    
