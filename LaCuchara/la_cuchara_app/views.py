import re
from django.shortcuts import render
from .forms import BusquedaForm
from .blob_storage import buscar_en_blobs

# Vista principal con enlace a búsqueda
def home(request):
    return render(request, 'la_cuchara_app/home.html')

def formatear_nombre_archivo(nombre_archivo):
    """
    Convierte un nombre de archivo en un formato más legible.
    Ejemplo: 'menu-Margarito_Ponzano-Bar.pdf.txt' -> 'Menú: Bar Margarito Ponzano'
    """
    # Quitar la extensión
    nombre_sin_extension = nombre_archivo.replace('.pdf.txt', '')

    # Separar partes por el guion
    partes = nombre_sin_extension.split('-')

    if len(partes) < 2:
        return nombre_archivo  # Si no sigue el formato esperado, devolver tal cual
    
    tipo_menu = partes[0].replace('_', ' ').capitalize()  # "menu_del_dia" -> "Menu del dia"
    nombre_lugar = ' '.join(partes[1:-1]).replace('_', ' ')  # Unir todas las partes intermedias
    tipo_lugar = partes[-1].replace('_', ' ')  # Tipo de lugar

    # Formatear el nombre
    nombre_formateado = f"{tipo_menu}: {tipo_lugar} {nombre_lugar}".replace("_", " ")

    # Devolver el nombre formateado
    return nombre_formateado

def buscar(request):
    resultados = []
    
    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            archivos = buscar_en_blobs(palabra_clave)

            # Formatear los nombres de los archivos
            resultados = [formatear_nombre_archivo(archivo) for archivo in archivos]
    
    else:
        form = BusquedaForm()
    
    return render(request, 'la_cuchara_app/buscar.html', {'form': form, 'resultados': resultados})
