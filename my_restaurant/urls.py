# djangotemplates/example/urls.py

from my_restaurant import views
from django.urls import path, include

urlpatterns = [
    
    path('about', views.AboutPageView.as_view(), name='about'),
    path('data', views.items_list, name='data'),
    path('', views.test.as_view(), name='home'),
    #path(r'^data/modify$', views.modifydata, name='data'),
    path('add_to_cart/<int:item_id>', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove_from_cart/<int:cart_item_id>', views.remove_from_cart, name='remove_from_cart'),
    path('add/<int:item_id>', views.add_to_cart_from_cart, name='add_to_cart_from_cart'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('cart_paid/<int:id>', views.cart_paid, name='cart_paid'),

    path('register', views.register_request, name="register"),
]