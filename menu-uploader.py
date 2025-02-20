from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv(override=True)

# Obtener la cadena de conexión de la cuenta de almacenamiento desde el archivo .env
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

if connect_str is None:
    print("Error: La cadena de conexión no está definida en el archivo .env.")
    exit()

# Crear el cliente del servicio Blob
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Define el contenedor en el que se van a almacenar las imágenes (asegúrate de que esté creado previamente)
container_name = 'menus'
container_client = blob_service_client.get_container_client(container_name)

# Función para subir archivos a Blob Storage
def subir_archivos_menu(ruta_carpeta):
    try:
        # Recorrer todos los archivos en la carpeta indicada
        for archivo in os.listdir(ruta_carpeta):
            archivo_path = os.path.join(ruta_carpeta, archivo)
            
            # Verificar que sea un archivo y no una carpeta
            if os.path.isfile(archivo_path):
                # Crear un cliente del Blob para cada archivo
                blob_client = container_client.get_blob_client(archivo)
                
                # Abrir el archivo en modo binario para subirlo
                with open(archivo_path, "rb") as data:
                    # Subir el archivo al Blob (con overwrite=True para permitir reemplazos)
                    blob_client.upload_blob(data, overwrite=True)
                
                # Retornar el enlace público del archivo subido
                print(f"Archivo {archivo} subido exitosamente.")
                print(f"Enlace del archivo subido: https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{archivo}")
                
    except Exception as e:
        print(f"Error al subir archivos: {e}")

# Ejemplo de uso
subir_archivos_menu("menus/")
