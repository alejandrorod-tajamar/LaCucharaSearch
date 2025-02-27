from django.urls import path
from la_cuchara_app import views

urlpatterns = [
    path('', views.home, name='home'),  # Página principal
    path('buscar/', views.buscar, name='buscar'),  # Página de búsqueda
    # Otras rutas
    path('consultar_reservas/', views.consultar_reservas, name='consultar_reservas'),
    path('promocionar_plato/', views.promocionar_plato, name='promocionar_plato'),
    path('reservar/', views.reservar, name='reservar'),
    path('restaurante_seleccionar/', views.restaurante_seleccionar, name='restaurante_seleccionar'),
    path('subir_menu/', views.subir_menu, name='subir_menu'),
    path('valorar_plato/', views.valorar_plato, name='valorar_plato'),
]
