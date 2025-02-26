from django import forms

class BusquedaForm(forms.Form):
    palabra_clave = forms.CharField(label='Buscar palabra clave', max_length=100)
