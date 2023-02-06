from django.db import models
from django.contrib.auth.models import User

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


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Menuitem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
