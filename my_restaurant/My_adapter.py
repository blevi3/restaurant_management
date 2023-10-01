from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from allauth.account.utils import perform_login
from django.shortcuts import redirect
from allauth.exceptions import ImmediateHttpResponse
from django.core.mail import EmailMessage
from .models import Profile  # Import the Profile model
import random
import string

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin): 
        print("adapteer")
        user = sociallogin.user
          
        try:
            customer = User.objects.get(email=user.email)  # if user exists, connect the account to the existing account and login
            active = customer.is_active
            print(customer)
            if active:
                sociallogin.state['process'] = 'connect'                
                perform_login(request, customer, 'none')
                print("login")
                raise ImmediateHttpResponse(redirect('home'))
            else:
               
                pw = randompw()
                message = "Szociális fiókhoz való csatolás miatt a jelszava az alábbira változott:\n {}\nKérjük ezt a jelszót mihamarabb változtassa meg!".format(pw)
                email = EmailMessage("Jelszó változás!", message ,to=[customer.email])
                email.send()
                customer.set_password(pw)                
                customer.is_active = True
                print(customer.is_active)
                customer.save()
                sociallogin.state['process'] = 'connect' 

                perform_login(request, customer, 'none')
                raise ImmediateHttpResponse(redirect('home'))
                
        except User.DoesNotExist:
            pw = randompw()
            username = self.generate_unique_username(user.email)
            user.username = username
            user.set_password(pw)
            user.save()
            Profile.objects.create(user=user)
            print("create")
            
            message = "A legenda étterem weboldalán regisztált, átmeneti jelszava:\n {}\nKérjük ezt a jelszót mihamarabb változtassa meg!".format(pw)
            email = EmailMessage("Jelszó változás!", message ,to=[user.email])
            email.send()
            perform_login(request, user, 'none')
            raise ImmediateHttpResponse(redirect('home'))


    def generate_unique_username(self, email):
        # Generate a unique username based on the email and a random string
        username = email.split('@')[0]
        while User.objects.filter(username=username).exists():
            # If the username already exists, add a random string
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            username = f"{username}_{random_string}"
        return username
def randompw():
        import random
        import string
        
        length = 12                      
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        num = string.digits
        symbols = string.punctuation
        all = lower + upper + num + symbols
        temp = random.sample(all,length)
        password = "".join(temp)
        
        return password