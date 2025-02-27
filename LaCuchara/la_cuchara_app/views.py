from django.shortcuts import render
from .forms import BusquedaForm
from .blob_storage import buscar_en_blobs
from .utils import formatear_nombre_archivo

# Vista principal
def home(request):
    return render(request, 'la_cuchara_app/home.html')

# Vista de búsqueda de menús
def buscar(request):
    resultados = []
    
    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            archivos = buscar_en_blobs(palabra_clave) or []  # Manejo de errores
            resultados = [formatear_nombre_archivo(archivo) for archivo in archivos]
    
    else:
        form = BusquedaForm()
    
    return render(request, 'la_cuchara_app/buscar.html', {'form': form, 'resultados': resultados})

# Vistas para restaurantes
def restaurante_seleccionar(request):  # Cambié el nombre de la función aquí
    return render(request, 'la_cuchara_app/restaurante_seleccionar.html')

def subir_menu(request):
    return render(request, 'la_cuchara_app/subir_menu.html')

def consultar_reservas(request):
    return render(request, 'la_cuchara_app/consultar_reservas.html')

def promocionar_plato(request):
    return render(request, 'la_cuchara_app/promocionar_plato.html')

# Vistas para usuarios
def valorar_plato(request):
    return render(request, 'la_cuchara_app/valorar_plato.html')

def reservar(request):
    return render(request, 'la_cuchara_app/reservar.html')
