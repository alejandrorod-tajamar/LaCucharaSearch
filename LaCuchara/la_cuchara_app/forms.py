from django import forms

class BuscarForm(forms.Form):
    query = forms.CharField(label='Buscar platos', max_length=100)

class ReservaForm(forms.Form):
    nombre_cliente = forms.CharField(max_length=100)
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

class PromocionForm(forms.Form):
    nombre_plato = forms.CharField(max_length=100)
    importe_promocion = forms.DecimalField(max_digits=10, decimal_places=2)