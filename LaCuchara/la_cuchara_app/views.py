from django.shortcuts import render, redirect
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from django.conf import settings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Conexión a MongoDB Atlas (sin modificar el servicio)
client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client.get_database(settings.DATABASES['default']['NAME'])
restaurantes = db.restaurantes

# Vista de inicio
def home(request):
    return render(request, 'la_cuchara_app/home.html')

# Flujo de Cliente

def buscar(request):
    query = request.POST.get('query', '') if request.method == 'POST' else ''
    tipo_menu = request.POST.get('tipo_menu', '')
    valoracion_min = float(request.POST.get('valoracion_min', 0))
    
    filtros = []
    if tipo_menu:
        filtros.append(f"tipo_menu eq '{tipo_menu}'")
    if valoracion_min > 0:
        filtros.append(f"platos/any(p: p/valoracion ge {valoracion_min})")
    
    resultados = []
    if request.method == 'POST':
        credential = AzureKeyCredential(settings.AZURE_SEARCH_KEY)
        client_search = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_INDEX_NAME,
            credential=credential
        )
        
        resultados = list(client_search.search(
            search_text=query,
            search_fields=["platos/nombre"],
            filter=" and ".join(filtros) if filtros else None,
            order_by=["max_promocion desc"],
            select=["id", "restaurante", "direccion", "platos", "tipo_menu"]
        ))
    
    # Filtrar localmente los platos que contienen la query en su nombre
    resultados_filtrados = []
    for restaurante in resultados:
        platos_coincidentes = [
            plato for plato in restaurante['platos']
            if query.lower() in plato['nombre'].lower()
        ]
        if platos_coincidentes:
            restaurante['platos'] = platos_coincidentes
            resultados_filtrados.append(restaurante)
    
    return render(request, 'la_cuchara_app/buscar.html', {
        'resultados': resultados_filtrados,
        'query': query,
        'tipo_menu_selected': tipo_menu,
        'valoracion_min': valoracion_min
    })

def reservar(request, restaurante_id):
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    
    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        try:
            nueva_reserva = {
                'nombre_cliente': nombre_cliente,
                'fecha': datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d'),
                'hora': datetime.strptime(hora, '%H:%M').strftime('%H:%M')
            }
        except ValueError:
            return render(request, 'la_cuchara_app/reservar.html', {
                'error': 'Formato de fecha/hora inválido',
                'restaurante': restaurante
            })
        
        # Comprobar que no exista ya una reserva en esa fecha y hora
        if any(r['fecha'] == nueva_reserva['fecha'] and r['hora'] == nueva_reserva['hora'] 
               for r in restaurante.get('reservas', [])):
            return render(request, 'la_cuchara_app/reservar.html', {
                'error': 'Horario no disponible',
                'restaurante': restaurante
            })
        
        restaurantes.update_one(
            {'_id': ObjectId(restaurante_id)},
            {'$push': {'reservas': nueva_reserva}}
        )
        return redirect('home')
    
    return render(request, 'la_cuchara_app/reservar.html', {'restaurante': restaurante})

def valorar_plato(request, restaurante_id, plato_nombre):
    if request.method == 'POST':
        try:
            new_rating = int(request.POST.get('puntuacion'))
            # Insertar la nueva valoración en el array "valoraciones" del plato.
            restaurantes.update_one(
                {'_id': ObjectId(restaurante_id), 'platos.nombre': plato_nombre},
                {'$push': {'platos.$.valoraciones': new_rating}}
            )
            # Recuperar el restaurante para recalcular el promedio del plato.
            restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
            for plato in restaurante.get('platos', []):
                if plato.get('nombre') == plato_nombre:
                    ratings = plato.get('valoraciones', [])
                    if ratings:
                        avg = sum(ratings) / len(ratings)
                        # Actualizar el campo "valoracion" del plato.
                        restaurantes.update_one(
                            {'_id': ObjectId(restaurante_id), 'platos.nombre': plato_nombre},
                            {'$set': {'platos.$.valoracion': round(avg, 1)}}
                        )
            return redirect('buscar')
        except Exception as e:
            print(f"Error al valorar: {e}")
    
    return render(request, 'la_cuchara_app/valorar_plato.html', {
        'restaurante_id': restaurante_id,
        'plato_nombre': plato_nombre
    })

# Flujo de Restaurante

def restaurante_seleccionar(request):
    if request.method == 'POST':
        restaurante_id = request.POST.get('restaurante_id')
        return redirect('opciones_restaurante', restaurante_id=restaurante_id)
    
    todos_restaurantes = list(restaurantes.find())
    for restaurante in todos_restaurantes:
        restaurante['id_str'] = str(restaurante['_id'])
    
    return render(request, 'la_cuchara_app/restaurante_seleccionar.html', {'restaurantes': todos_restaurantes})

def opciones_restaurante(request, restaurante_id):
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    restaurante['id_str'] = str(restaurante['_id'])
    return render(request, 'la_cuchara_app/opciones_restaurante.html', {'restaurante': restaurante})

def promocionar_plato(request, restaurante_id):
    if request.method == 'POST':
        nombre_plato = request.POST.get('nombre_plato')
        importe = float(request.POST.get('importe'))
        
        # Insertar la promoción en el array de promociones del plato.
        restaurantes.update_one(
            {'_id': ObjectId(restaurante_id), 'platos.nombre': nombre_plato},
            {'$push': {'platos.$.promocion': {
                'importe': importe,
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d')
            }}}
        )
        # Actualizar (o establecer) el campo 'promocion_importe' para que el plato muestre la promoción.
        restaurantes.update_one(
            {'_id': ObjectId(restaurante_id), 'platos.nombre': nombre_plato},
            {'$set': {'platos.$.promocion_importe': importe}}
        )
        return redirect('opciones_restaurante', restaurante_id=restaurante_id)
    
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    restaurante['id_str'] = str(restaurante['_id'])
    return render(request, 'la_cuchara_app/promocionar_plato.html', {'restaurante': restaurante})
    
def consultar_reservas(request, restaurante_id):
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    restaurante['id_str'] = str(restaurante['_id'])  # ← Añadir esta línea
    reservas = restaurante.get('reservas', [])
    return render(request, 'la_cuchara_app/consultar_reservas.html', {
        'reservas': reservas,
        'restaurante': restaurante  # ← Asegurar que se pasa el restaurante con id_str
    })
