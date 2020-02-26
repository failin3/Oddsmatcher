from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.auth_view, name='index'),
]
