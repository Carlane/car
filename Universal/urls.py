from django.conf.urls import url
from Universal import views

urlpatterns = [
    url(r'^CarInfo/(?P<pk>[0-9]+)/$', views.cardetails),
    url(r'^UserSignUp/$', views.usersignup),
    url(r'^addr/(?P<pk>[0-9]+)/$', views.address),
    url(r'^request/(?P<pk>[0-9]+)/$', views.initiate_request),
]
