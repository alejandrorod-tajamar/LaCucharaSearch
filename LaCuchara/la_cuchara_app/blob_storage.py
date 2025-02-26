from azure.storage.blob import BlobServiceClient
from django.conf import settings

def buscar_en_blobs(palabra_clave):
    # Conectar al Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client('menus-txt')
    
    resultados = []
    
    # Iterar sobre los blobs (archivos txt)
    for blob in container_client.list_blobs():
        # Descargar el contenido del blob
        blob_client = container_client.get_blob_client(blob)
        contenido = blob_client.download_blob().readall().decode('utf-8')
        
        # Verificar si la palabra clave está en el contenido del archivo
        if palabra_clave.lower() in contenido.lower():
            resultados.append(blob.name)  # Almacenar el nombre del archivo donde se encontró la palabra clave
    
    return resultados
