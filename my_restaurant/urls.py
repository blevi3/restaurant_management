# djangotemplates/example/urls.py

from my_restaurant import views
from django.urls import path, include

urlpatterns = [
    
    path('about', views.AboutPageView.as_view(), name='about'),
    path('data', views.items_list, name='data'),
    path('', views.test.as_view(), name='home'),
    #path(r'^data/modify$', views.modifydata, name='data'),
    path(r'^register/$', views.register_request, name="register"),
]