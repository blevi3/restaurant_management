from django.db import models
from django.contrib.auth.models import User


User._meta.get_field('email')._unique = True
User._meta.get_field('username')._unique = True
# Create your models here.
class Menuitem(models.Model):
    name = models.CharField(max_length=100)
    type = models.BooleanField()
    category = models.CharField(max_length=100)
    price = models.IntegerField()
    def __str__(self):
        return f"{self.name, self.type, self.category, self.price}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_to_be_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ordered = models.BooleanField(default=0)
    is_delivered = models.BooleanField(default=0)
    is_paid = models.BooleanField(default=False)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Menuitem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class Table(models.Model):
    name = models.CharField(max_length=50)
    max_capacity = models.IntegerField()

    def __str__(self):
        return self.name
    
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    party_size = models.IntegerField(validators=[MinValueValidator(1)])
    


    def __str__(self):
        
        return f"{self.name} at Table {self.table} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=254)
    def __str__(self):
        return self.user.username, self.user.email



