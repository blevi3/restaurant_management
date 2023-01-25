from django.db import models

# Create your models here.
class Menuitem(models.Model):
    name = models.CharField(max_length=100)
    type = models.BooleanField()
    category = models.CharField(max_length=100)
    price = models.IntegerField()
    def __str__(self):
        return f"{self.name, self.type, self.category, self.price}"
