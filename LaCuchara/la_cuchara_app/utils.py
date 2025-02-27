import re

def formatear_nombre_archivo(nombre):
    # Eliminar la extensión '.pdf.txt' del nombre del archivo
    nombre_sin_extension = nombre.replace(".pdf.txt", "")
    
    # Determinar si es carta o menú
    tipo = "Carta" if "carta" in nombre_sin_extension else "Menú"
    
    # Extraer el nombre del restaurante (se encuentra después de la palabra clave)
    # Usamos una expresión regular para dividir por guiones y obtener el nombre limpio
    nombre_partes = nombre_sin_extension.split('-')[1:]
    nombre_restaurante = " ".join(nombre_partes).replace("_", " ").title()
    
    # Crear un formato bonito
    nombre_formateado = f"{tipo}: {nombre_restaurante}"
    
    return nombre_formateado
