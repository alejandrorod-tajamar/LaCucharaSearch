import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Cargar variables de entorno
load_dotenv(override=True)

# Configuración de Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")
AZURE_STORAGE_NAME = os.getenv("AZURE_STORAGE_NAME")

# Cliente de Document Intelligence
document_analysis_client = DocumentAnalysisClient(AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_API_KEY))

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

# PRUEBA con un archivo del Blob Storage
blob_name = "<nombre_del_archivo_en_blob>"
texto_extraido = extract_text_from_blob(blob_name)
print(texto_extraido)
