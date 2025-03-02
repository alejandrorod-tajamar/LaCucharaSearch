from django.db import models

class Valoracion(models.Model):
    plato_id = models.CharField(max_length=100)  # ID del plato en MongoDB
    usuario = models.CharField(max_length=100)
    puntuacion = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    fecha = models.DateTimeField(auto_now_add=True)