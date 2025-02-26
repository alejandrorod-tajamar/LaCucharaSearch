from django.shortcuts import render
from django.http import HttpResponse
from .forms import BusquedaForm
from .blob_storage import buscar_en_blobs

# Vista principal con enlace a búsqueda
def home(request):
    return render(request, 'la_cuchara_app/home.html')

def buscar(request):
    resultados = []
    
    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            # Llamar a la función de búsqueda en los blobs
            resultados = buscar_en_blobs(palabra_clave)
    
    else:
        form = BusquedaForm()
    
    return render(request, 'la_cuchara_app/buscar.html', {'form': form, 'resultados': resultados})
