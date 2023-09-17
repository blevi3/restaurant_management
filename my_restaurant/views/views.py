from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test

def staff_member_required(view_func):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/accounts/login/',
        redirect_field_name='next'
    )
    return actual_decorator(view_func)

def gallery(request):
    return render(request, 'gallery.html' )

class HomePageView(TemplateView):
    template_name = "index.html"


class AboutPageView(TemplateView):
    template_name = "about.html"

class home(TemplateView):
    template_name = "home.html"


class Testpage(TemplateView):
    template_name = "index.html"





