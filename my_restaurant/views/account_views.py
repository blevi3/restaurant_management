from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from ..forms import UserUpdateForm, NewUserForm
from ..models import Coupons, Profile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.http import HttpResponse
from django.contrib.auth import login


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
    user_coupons = Coupons.objects.filter(user_id=request.user.id)
    context = {
        'user_form': user_form,
        'points': Profile.objects.get(user=request.user).points,
        'user_coupons': user_coupons,
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

