from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from ..models import Profile

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

from django.utils import translation
from django.shortcuts import redirect

def change_language(request):
    if request.method == 'POST':
        new_language = request.POST.get('language')
        language_codes = [choice[0] for choice in Profile.LANGUAGE_CHOICES]        
        new_language_code = new_language.split(',')[0].strip('()\'"')
        
        if new_language_code in language_codes:
            request.user.profile.language = new_language_code
            request.user.profile.save()
            translation.activate(new_language_code)
    
    redirect_url = request.META.get('HTTP_REFERER')
    
    if not redirect_url:
        redirect_url = 'home'
    
    return redirect(redirect_url)
