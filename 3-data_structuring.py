import os
import json
import requests
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
from pymongo import MongoClient
import re
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv(override=True)

def obtener_texto_desde_blob(blob_name):
    """Descarga el contenido de un archivo .txt desde Azure Blob Storage."""
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    container_client = blob_service_client.get_container_client("menus-txt")
    blob_client = container_client.get_blob_client(blob_name)
    
    return blob_client.download_blob().readall().decode("utf-8")

def limpiar_respuesta_json(response_content):
    """Elimina las comillas triples y cualquier texto extra."""
    response_content = re.sub(r'```json', '', response_content)
    response_content = re.sub(r'```', '', response_content)
    return response_content.strip()

def buscar_direccion_y_coordenadas(nombre_restaurante):
    """Busca la dirección y coordenadas de un restaurante usando Azure Maps, limitando la búsqueda a Madrid."""
    azure_maps_key = os.getenv("AZURE_MAPS_API_KEY")
    # Añade '&countrySet=ES&view=Auto&limit=1&typeahead=true&lat=40.4168&lon=-3.7038&radius=10000' para centrar la búsqueda en Madrid
    url = f"https://atlas.microsoft.com/search/poi/json?api-version=1.0&query={nombre_restaurante}&subscription-key={azure_maps_key}&countrySet=ES&lat=40.4168&lon=-3.7038&radius=10000"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Obtener la primera coincidencia de la respuesta
        if data.get("results") and len(data["results"]) > 0:
            resultado = data["results"][0]
            direccion = resultado["address"]["freeformAddress"]
            latitud = resultado["position"]["lat"]
            longitud = resultado["position"]["lon"]
            return direccion, latitud, longitud
        else:
            print(f"No se encontraron resultados para el restaurante: {nombre_restaurante}")
            return None, None, None
    except Exception as e:
        print(f"Error al buscar dirección y coordenadas en Azure Maps: {e}")
        return None, None, None

def estructurar_texto_con_openai(texto):
    """Envía el texto a Azure OpenAI para estructurarlo en formato JSON."""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            Tu tarea es extraer la información de un menú en un formato JSON. Por favor, solo devuelve el JSON, sin texto adicional ni explicaciones. El JSON debe ser válido y contener los siguientes campos:
            - restaurante: Nombre del restaurante (Lo pone en el nombre del archivo).
            - tipologia: Tipo o estilo del restaurante (Meidterráneo, Tradicional, etc.).
            - tipo_menu: Si tienen algún plato que sea alguna opción de las siguientes: (sin_restricciones, opciones_celiacos, opciones_vegetarianas, opciones_veganas, ...)
            - valoracion: Valoración del restaurante (1-5) (Invéntatela).
            - reservas: Las reservas activas asociadas al restaurante (un array vacío).
            - platos: Un array de objetos, donde cada objeto representa un plato y contiene:
                - nombre: Nombre del plato.
                - tipo: Tipo de plato (Entrante, Principal, Postre o Carta [si no es ninguno de los anteriores]).
                - valoracion: Valoración del plato (1-5) (Invéntatela).
                - precio: Precio del plato como número (sin símbolo de moneda).
                - moneda: Moneda en la que está expresado el precio (por ejemplo, "EUR").
                - ingredientes: Array de ingredientes del plato.
                - promocion: Las promociones activas asociadas al plato (un array vacío).
            """},
            {"role": "user", "content": texto}
        ]
    )
    
    response_content = response.choices[0].message.content
    cleaned_content = limpiar_respuesta_json(response_content)
    
    try:
        return json.loads(cleaned_content)
    except json.JSONDecodeError:
        print(f"Error al decodificar la respuesta JSON de OpenAI: {cleaned_content}")
        return None

def guardar_en_mongodb(datos_json):
    """Guarda los datos estructurados en MongoDB Atlas."""
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.get_database("LaCucharaDB")
    collection = db.get_collection("restaurantes")
    
    collection.insert_one(datos_json)

def procesar_archivo(blob_name):
    """Proceso completo: extraer, estructurar y almacenar un archivo."""
    texto = obtener_texto_desde_blob(blob_name)
    datos_json = estructurar_texto_con_openai(texto)
    
    if datos_json:
        # Obtener dirección y coordenadas del restaurante usando Azure Maps
        nombre_restaurante = datos_json.get("restaurante")
        if nombre_restaurante:
            direccion, latitud, longitud = buscar_direccion_y_coordenadas(nombre_restaurante)
            if direccion and latitud and longitud:
                datos_json["direccion"] = direccion
                datos_json["ubicacion"] = {
                    "type": "Point",
                    "coordinates": [longitud, latitud]  # MongoDB usa [longitud, latitud]
                }
        
        # Guardar en MongoDB
        guardar_en_mongodb(datos_json)
        print(f"Archivo {blob_name} procesado correctamente.")
    else:
        print(f"Error al procesar el archivo {blob_name}.")

def procesar_todos_los_archivos():
    """Procesa todos los archivos .txt en el contenedor de Blob Storage."""
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    container_client = blob_service_client.get_container_client("menus-txt")
    
    # Obtener todos los archivos .txt en el contenedor
    blobs = container_client.list_blobs()
    for blob in blobs:
        if blob.name.endswith(".txt"):
            procesar_archivo(blob.name)

# Ejecutar el procesamiento de todos los archivos .txt
if __name__ == "__main__":
    procesar_todos_los_archivos()
