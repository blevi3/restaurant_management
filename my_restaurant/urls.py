# djangotemplates/example/urls.py

from my_restaurant import views
from django.urls import path, include


urlpatterns = [
    
    path('about', views.AboutPageView.as_view(), name='about'),
    path('order', views.items_list, name='order'),
    path('', views.home.as_view(), name='home'),
    #path(r'^data/modify$', views.modifydata, name='data'),
    path('add_to_cart/<int:item_id>', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('previous_orders/', views.previous_orders, name='previous_orders'),
    path('remove_from_cart/<int:cart_item_id>', views.remove_from_cart, name='remove_from_cart'),
    path('remove_item/<int:cart_item_id>', views.trash_item, name='trash_item'),
    path('empty_cart/', views.empty_cart, name='empty_cart'),
    path('add/<int:item_id>', views.add_to_cart_from_cart, name='add_to_cart_from_cart'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('cart_delivered/<int:id>', views.cart_delivered, name='cart_delivered'),
    path('order/<int:id>', views.order, name='order'),
    path('order_paid_admin/<int:id>', views.order_paid_admin, name='order_paid_admin'),
    path('order_paid/<int:id>', views.order_paid, name='order_paid'),
    path('accounts/register', views.register_request, name="register"),
    path('drinks', views.drinks, name='drinks'),
    path('menu', views.menu, name='menu'),
    path('all_reservations', views.all_reservations, name = "all_reservations"),
    path('my_reservations', views.my_reservations, name = "my_reservations"),

    #path('date_selection/', views.date_selection, name='date_selection'),
    #path('available_tables/', views.available_tables, name='available_tables'),
    path('tables/', views.available_tables, name='available_tables'),
    path('reservation/<int:table_id>/<str:date1>', views.reservation_table, name='reservation_table'),
    path('password_reset/', views.password_reset_request, name="password_reset"),
    path('profile/', views.profile, name='profile'),

    path('payment/', views.payment, name='payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
]