from django.urls import path
from .views import home, buscar

urlpatterns = [
    path('', home, name='home'),  # Página principal
    path('buscar/', buscar, name='buscar'),  # Página de búsqueda
]
