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
    nombre_archivo = nombre_archivo.replace(".pdf.txt", "")

    # Separar partes por el guion
    partes = nombre_archivo.split('-')

    if len(partes) < 2:
        return nombre_archivo  # Devolver sin cambios si el formato no es válido
    
    tipo_menu = partes[0]  # 'menu', 'carta', etc.
    nombre_lugar = partes[1:-1]  # El nombre del sitio
    tipo_lugar = partes[-1]  # 'Restaurante', 'Bar', etc.

    # Reemplazar guiones bajos por espacios en el nombre del lugar
    nombre_lugar = " ".join(nombre_lugar).replace("_", " ")

    # Convertir el tipo de menú a un formato más bonito
    tipo_menu = tipo_menu.capitalize().replace("_", " ")  # 'menu_del_dia' -> 'Menu del dia'

    # Formatear el resultado
    return f"{tipo_menu}: {tipo_lugar} {nombre_lugar}"

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
