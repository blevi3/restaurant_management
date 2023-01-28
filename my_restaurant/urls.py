# djangotemplates/example/urls.py

from my_restaurant import views
from django.urls import path, include

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'), # Notice the URL has been named
    path(r'^about/$', views.AboutPageView.as_view(), name='about'),
    path(r'^data/$', views.items_list, name='data'),
    
    #path(r'^data/modify$', views.modifydata, name='data'),
    path(r'^register/$', views.register_request, name="register"),
]