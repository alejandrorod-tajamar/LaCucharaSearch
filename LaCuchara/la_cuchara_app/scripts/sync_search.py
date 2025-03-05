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
    if isinstance(text, (list, dict)):
        return text
    return text.encode('utf-8', 'ignore').decode('utf-8') if isinstance(text, str) else str(text)

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
            
            # Procesar platos y promociones
            for plato in restaurante.get('platos', []):
                promociones = plato.get('promocion', [{}])
                promo_importe = max((p.get('importe', 0) for p in promociones), default=0)
                
                if promo_importe > max_promo:
                    max_promo = promo_importe
                
                platos_procesados.append({
                    'nombre': clean_string(plato.get('nombre', '')),
                    'promocion_importe': promo_importe,
                    'valoracion': float(plato.get('valoracion', 0))
                })
            
            # Procesar tipo_menu como array
            tipo_menu = restaurante.get('tipo_menu', 'sin_restricciones')
            if isinstance(tipo_menu, str):
                tipo_menu = [tipo_menu.strip()] if tipo_menu.strip() else ['sin_restricciones']
            elif isinstance(tipo_menu, list):
                tipo_menu = [clean_string(tm).strip() for tm in tipo_menu if tm.strip()]
            else:
                tipo_menu = ['sin_restricciones']
            
            # Valoración del restaurante
            valoracion_rest = float(restaurante.get('valoracion', 0))
            
            # Construir documento para Azure
            doc = {
                'id': str(restaurante['_id']),
                'restaurante': clean_string(restaurante.get('restaurante', '')),
                'direccion': clean_string(restaurante.get('direccion', '')),
                'tipo_menu': tipo_menu,
                'valoracion': valoracion_rest,
                'max_promocion': max_promo,
                'platos': platos_procesados
            }
            documentos.append(doc)
            
        except Exception as e:
            print(f"Error procesando {restaurante.get('restaurante', '')}: {str(e)}")
            continue
    
    # Subir a Azure
    if documentos:
        try:
            result = client_azure.upload_documents(documents=documentos)
            print(f"✅ Sincronizados {len(documentos)} restaurantes")
            print(f"Resultado Azure: {result[0].succeeded}")
        except Exception as e:
            print(f"🚨 Error al subir documentos: {str(e)}")
    else:
        print("⚠️ No hay datos para sincronizar")

if __name__ == "__main__":
    sync_data()