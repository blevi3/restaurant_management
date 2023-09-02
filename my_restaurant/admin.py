from django.contrib import admin
from my_restaurant.models import Cart, CartItem, Menuitem, Table, Reservation
from django.contrib.auth.models import User
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Menuitem)
class MenuItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    pass

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    pass

