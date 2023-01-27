# djangotemplates/example/urls.py

from django.conf.urls import url
from my_restaurant import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name='home'), # Notice the URL has been named
    url(r'^about/$', views.AboutPageView.as_view(), name='about'),
    url(r'^data/$', views.items_list, name='data'),
    
    #url(r'^data/modify$', views.modifydata, name='data'),
    url(r'^register/$', views.register_request, name="register"),
]