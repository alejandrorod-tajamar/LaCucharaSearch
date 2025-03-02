import os
import sys
import django
from pymongo import MongoClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from django.conf import settings
from bson import ObjectId

# Configurar entorno Django
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LaCuchara.settings')
django.setup()

def clean_string(text):
    """Limpia caracteres no válidos para Azure"""
    return text.encode('utf-8', 'ignore').decode('utf-8') if isinstance(text, str) else text

def sync_data():
    # Conexión a MongoDB
    client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
    db = client_mongo.get_database(settings.DATABASES['default']['NAME'])
    restaurantes_col = db.restaurantes
    
    # Conexión a Azure
    credential = AzureKeyCredential(settings.AZURE_SEARCH_KEY)
    client_azure = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_INDEX_NAME,
        credential=credential
    )
    
    documentos = []
    for restaurante in restaurantes_col.find():
        try:
            max_promo = 0
            platos_procesados = []
            
            for plato in restaurante.get('platos', []):
                # Procesar promoción
                promociones = plato.get('promocion', [{}])
                promo_importe = promociones[0].get('importe', 0) if promociones else 0
                
                # Actualizar máximo
                if promo_importe > max_promo:
                    max_promo = promo_importe
                
                platos_procesados.append({
                    'nombre': clean_string(plato.get('nombre', '')),
                    'promocion_importe': promo_importe,
                    'valoracion': plato.get('valoracion', 0)
                })
            
            # Validar y asignar valor predeterminado para tipo_menu
            tipo_menu = restaurante.get('tipo_menu', '')
            
            # Si tipo_menu es una lista, convertirla a cadena
            if isinstance(tipo_menu, list):
                tipo_menu = ', '.join(tipo_menu)  # Unir elementos de la lista con comas
            elif not isinstance(tipo_menu, str):  # Si no es una cadena ni una lista
                tipo_menu = str(tipo_menu)  # Convertir a cadena
            
            # Eliminar espacios en blanco al principio y al final
            tipo_menu = tipo_menu.strip()
            
            # Si está vacío, asignar valor predeterminado
            if not tipo_menu:
                tipo_menu = 'sin_restricciones'
            
            # Construir documento para Azure
            doc = {
                'id': str(restaurante['_id']),
                'restaurante': clean_string(restaurante.get('restaurante', '')),
                'direccion': clean_string(restaurante.get('direccion', '')),
                'tipo_menu': clean_string(tipo_menu),  # Usar el valor validado
                'max_promocion': max_promo,
                'platos': platos_procesados
            }
            documentos.append(doc)
            
        except Exception as e:
            print(f"Error procesando {restaurante.get('restaurante', '')}: {str(e)}")
    
    # Subir a Azure
    if documentos:
        try:
            client_azure.upload_documents(documents=documentos)
            print(f"✅ {len(documentos)} restaurantes sincronizados")
        except Exception as e:
            print(f"Error al subir documentos a Azure: {str(e)}")
    else:
        print("⚠️ No hay datos para sincronizar")

if __name__ == "__main__":
    sync_data()