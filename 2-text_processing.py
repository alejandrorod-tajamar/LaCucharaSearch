import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

# Cargar variables de entorno
load_dotenv(override=True)

# Configuración de Azure Document Intelligence y Blob Storage
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")
AZURE_STORAGE_NAME = os.getenv("AZURE_STORAGE_NAME")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")  # Agrega esta variable

# Cliente de Document Intelligence
document_analysis_client = DocumentAnalysisClient(AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_API_KEY))

# Cliente de Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
menus_container_client = blob_service_client.get_container_client('menus')  # Contenedor de menús
menus_txt_container_client = blob_service_client.get_container_client('menus-txt')  # Contenedor de textos extraídos

# Verificar si el contenedor 'menus-txt' existe, y si no, crearlo
try:
    menus_txt_container_client.get_container_properties()
    print("El contenedor 'menus-txt' ya existe.")
except Exception:
    print("El contenedor 'menus-txt' no existe. Creando contenedor...")
    blob_service_client.create_container('menus-txt')
    print("Contenedor 'menus-txt' creado.")

def extract_text_from_blob(blob_name):
    """Extrae el texto de un archivo en Blob Storage usando Azure Document Intelligence."""
    blob_url = f"https://{AZURE_STORAGE_NAME}.blob.core.windows.net/menus/{blob_name}"
    
    try:
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", blob_url)
        result = poller.result()
        extracted_text = "\n".join([line.content for page in result.pages for line in page.lines])
        return extracted_text
    except Exception as e:
        print(f"Error procesando {blob_name}: {e}")
        return None

def save_text_to_blob(blob_name, text):
    """Guarda el texto extraído en un archivo en el contenedor 'menus-txt'."""
    blob_client = menus_txt_container_client.get_blob_client(f"{blob_name}.txt")
    blob_client.upload_blob(text, overwrite=True)
    print(f"Texto guardado en menus-txt/{blob_name}.txt")

def process_all_blobs():
    """Recorre todos los archivos en el contenedor de menús y guarda los textos extraídos en el contenedor 'menus-txt'."""
    for blob in menus_container_client.list_blobs():
        blob_name = blob.name
        print(f"Procesando archivo: {blob_name}")
        
        # Extraer texto del archivo
        extracted_text = extract_text_from_blob(blob_name)
        if extracted_text:
            # Guardar texto extraído en el contenedor 'menus-txt'
            save_text_to_blob(blob_name, extracted_text)

# Llamar a la función para procesar todos los archivos
process_all_blobs()
