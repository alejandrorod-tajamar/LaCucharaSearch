from django.db import models

class Valoracion(models.Model):
    plato_id = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100)
    puntuacion = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plato_id} - {self.usuario}: {self.puntuacion}"
