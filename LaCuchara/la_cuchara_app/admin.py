from django.contrib import admin

# Register your models here.
from .models import Restaurante, Menu, Plato, ValoracionRestaurante, ValoracionPlato, Promocion, Reserva

admin.site.register(Restaurante)
admin.site.register(Menu)
admin.site.register(Plato)
admin.site.register(ValoracionRestaurante)
admin.site.register(ValoracionPlato)
admin.site.register(Promocion)
admin.site.register(Reserva)
