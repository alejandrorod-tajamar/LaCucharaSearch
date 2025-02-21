from django.db import models

# Create your models here.

class Restaurante(models.Model):
    nombre      = models.CharField(max_length=255)
    direccion   = models.TextField()
    ubicacion   = models.CharField(max_length=255, help_text="Ciudad o zona")
    tipologia   = models.CharField(max_length=100, help_text="Ej. Mediterráneo, Vegano, etc.")
    telefono    = models.CharField(max_length=20, blank=True, null=True)
    email       = models.EmailField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Menu(models.Model):
    TIPO_CHOICES = [
        ('menu', 'Menú Diario'),
        ('carta', 'Carta'),
    ]
    
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="menus")
    tipo        = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha       = models.DateField(help_text="Fecha para la que aplica el menú", null=True, blank=True)
    platos      = models.JSONField(help_text="Lista de platos con detalles (nombre, precio, restricciones, etc.)", blank=True, null=True)
    archivo_url = models.URLField(help_text="URL del archivo almacenado en Blob Storage")
    updated_at  = models.DateTimeField(auto_now=True)  # Guarda la última actualización

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.restaurante.nombre} - {self.fecha if self.fecha else 'Sin fecha'}"

class Plato(models.Model):
    CATEGORIA_CHOICES = [
        ('entrante', 'Entrante'),
        ('principal', 'Principal'),
        ('postre', 'Postre'),
    ]
    
    nombre         = models.CharField(max_length=255)
    descripcion    = models.TextField(blank=True, null=True)
    precio         = models.DecimalField(max_digits=6, decimal_places=2)
    categoria      = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    # Restricciones: por ejemplo, sin gluten, vegetariano, vegano, etc.
    restricciones  = models.CharField(max_length=100, blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class ValoracionRestaurante(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="valoraciones")
    usuario     = models.CharField(max_length=255, help_text="Identificador del comensal")
    puntuacion  = models.IntegerField(help_text="Valoración numérica (por ejemplo, 1-5)")
    comentario  = models.TextField(blank=True, null=True)
    fecha       = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Valoración de {self.usuario} para {self.restaurante.nombre}"

class ValoracionPlato(models.Model):
    plato      = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name="valoraciones")
    usuario    = models.CharField(max_length=255, help_text="Identificador del comensal")
    puntuacion = models.IntegerField(help_text="Valoración numérica (1-5)")
    comentario = models.TextField(blank=True, null=True)
    fecha      = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Valoración de {self.usuario} para {self.plato.nombre}"

class Promocion(models.Model):
    plato            = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name="promociones")
    restaurante      = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="promociones")
    precio_promocional = models.DecimalField(max_digits=6, decimal_places=2)
    fecha_inicio     = models.DateTimeField()
    fecha_fin        = models.DateTimeField()
    importe_diario   = models.DecimalField(max_digits=6, decimal_places=2, help_text="Importe pagado diariamente")
    
    def __str__(self):
        return f"Promoción para {self.plato.nombre} en {self.restaurante.nombre}"

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    usuario       = models.CharField(max_length=255, help_text="Identificador del comensal")
    restaurante   = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="reservas")
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    # Almacenar la selección de platos: se puede usar un JSONField para simplificar
    platos        = models.JSONField(help_text="Listado de platos solicitados", blank=True, null=True)
    estado        = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    def __str__(self):
        return f"Reserva de {self.usuario} en {self.restaurante.nombre}"
