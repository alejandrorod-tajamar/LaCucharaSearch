# la_cuchara_app/urls.py
from django.urls import path

from . import views
from .views import buscar

urlpatterns = [
    path('', views.home, name='home'),
    path('buscar/', buscar, name='buscar'),
]
