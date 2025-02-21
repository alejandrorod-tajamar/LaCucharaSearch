from django.contrib import admin

from .models import Restaurante, Menu, Plato, ValoracionRestaurante, ValoracionPlato, Promocion, Reserva

# Register your models here.
admin.site.register(Restaurante)
admin.site.register(Menu)
admin.site.register(Plato)
admin.site.register(ValoracionRestaurante)
admin.site.register(ValoracionPlato)
admin.site.register(Promocion)
admin.site.register(Reserva)
