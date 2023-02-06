from django.contrib import admin
from my_restaurant.models import Cart, CartItem, Menuitem
# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Menuitem)
class MenuItemAdmin(admin.ModelAdmin):
    pass