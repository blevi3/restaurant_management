from django.contrib import admin
from my_restaurant.models import Cart, CartItem, Menuitem, Table, Reservation , Coupons, Qr_code_reads
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

@admin.register(Coupons)
class CouponAdmin(admin.ModelAdmin):
    pass

@admin.register(Qr_code_reads)
class QrCodeAdmin(admin.ModelAdmin):
    pass