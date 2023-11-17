from django.db import models
from django.contrib.auth.models import User


User._meta.get_field('email')._unique = True
User._meta.get_field('username')._unique = True
class Menuitem(models.Model):
    name = models.CharField(max_length=100)
    type = models.BooleanField()
    category = models.CharField(max_length=100)
    price = models.IntegerField()
    def __str__(self):
        return f"{self.name, self.type, self.category, self.price}"
    
class Coupons(models.Model):
    COUPON_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ]

    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default='percentage')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    code = models.CharField(max_length=20)
    product = models.CharField(max_length=40, default="null", null=True)
    is_unique = models.BooleanField(default=False)
    user_id =  models.IntegerField(default=0)

    def __str__(self):
        return self.code

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_to_be_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ordered = models.BooleanField(default=0)
    is_delivered = models.BooleanField(default=0)
    is_paid = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)
    table = models.CharField(max_length=50, default="null")
    applied_coupon_type = models.CharField(max_length=10, blank=True, null=True)
    reduced_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_time = models.DateTimeField(blank=True, null=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Menuitem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(blank=True, null=True)

class Table(models.Model):
    name = models.CharField(max_length=50)
    max_capacity = models.IntegerField()

    def __str__(self):
        return self.name
    
class Qr_code_reads(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_time = models.DateTimeField(null=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=0)
    finalized = models.BooleanField(default=0)
    
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
    taken = models.BooleanField(default=False)
    
    def __str__(self):
        
        return f"{self.name} at Table {self.table} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  unique=True)
    username = models.CharField(max_length=30, help_text="")
    email = models.EmailField(max_length=254)
    points = models.IntegerField(default=0)
    LANGUAGE_CHOICES = (
    ('en-us', 'English'),
    ('nl', 'Dutch'),    
    ('hu', 'Hungarian')
    )

    language = models.CharField(default='hu', choices=LANGUAGE_CHOICES, max_length=5)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    code = models.CharField(max_length=20)
    products =models.CharField(max_length=40, default="null")
    is_unique = models.BooleanField(default=False)

    def __str__(self):
        return self.name


