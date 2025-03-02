from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('buscar/', views.buscar, name='buscar'),
    path('reservar/<str:restaurante_id>/', views.reservar, name='reservar'),
    path('restaurante/', views.restaurante_seleccionar, name='restaurante_seleccionar'),
    path('restaurante/<str:restaurante_id>/opciones/', views.opciones_restaurante, name='opciones_restaurante'),
    path('restaurante/<str:restaurante_id>/promocionar/', views.promocionar_plato, name='promocionar_plato'),
    path('restaurante/<str:restaurante_id>/reservas/', views.consultar_reservas, name='consultar_reservas'),
    path('valorar/<str:restaurante_id>/<str:plato_nombre>/', views.valorar_plato, name='valorar_plato'),
]