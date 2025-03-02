from django.shortcuts import render, redirect
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from django.conf import settings
from .forms import *
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Conexión MongoDB Atlas
client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client.get_database(settings.DATABASES['default']['NAME'])
restaurantes = db.restaurantes

# Vistas comunes
def home(request):
    return render(request, 'la_cuchara_app/home.html')  # Asegúrate de que la ruta sea correcta

# Flujo Restaurante
def restaurante_seleccionar(request):
    if request.method == 'POST':
        restaurante_id = request.POST.get('restaurante_id')
        return redirect('opciones_restaurante', restaurante_id=restaurante_id)
    
    todos_restaurantes = list(restaurantes.find())
    
    # Convertir _id a string para cada restaurante
    for restaurante in todos_restaurantes:
        restaurante['id_str'] = str(restaurante['_id'])  # Nuevo campo
    
    return render(request, 'la_cuchara_app/restaurante_seleccionar.html', {'restaurantes': todos_restaurantes})

def opciones_restaurante(request, restaurante_id):
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    # Convertir _id a string
    restaurante['id_str'] = str(restaurante['_id'])
    return render(request, 'la_cuchara_app/opciones_restaurante.html', {'restaurante': restaurante})

def promocionar_plato(request, restaurante_id):
    if request.method == 'POST':
        nombre_plato = request.POST.get('nombre_plato')
        importe = float(request.POST.get('importe'))
        
        # Actualizar MongoDB
        restaurantes.update_one(
            {'_id': ObjectId(restaurante_id), 'platos.nombre': nombre_plato},
            {'$push': {'platos.$.promocion': {
                'importe': importe,
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d')
            }}}
        )
        
        # Sincronizar con Azure AI Search
        #sync_data()  # Tu función de sincronización
        
        return redirect('opciones_restaurante', restaurante_id=restaurante_id)
    
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    return render(request, 'promocionar_plato.html', {'restaurante': restaurante})

def consultar_reservas(request, restaurante_id):
    restaurante = restaurantes.find_one({'_id': ObjectId(restaurante_id)})
    return render(request, 'la_cuchara_app/consultar_reservas.html', {
        'reservas': restaurante.get('reservas', []),
        'restaurante': restaurante
    })

# Flujo Cliente

def buscar(request):
    query = request.POST.get('query', '') if request.method == 'POST' else ''
    tipo_menu = request.POST.get('tipo_menu', '')
    valoracion_min = float(request.POST.get('valoracion_min', 0))
    
    # Construir filtro para Azure
    filtros = []
    if tipo_menu:
        filtros.append(f"tipo_menu eq '{tipo_menu}'")
    if valoracion_min > 0:
        filtros.append(f"platos/any(p: p/valoracion ge {valoracion_min})")
    
    # Realizar búsqueda
    resultados = []
    if request.method == 'POST':
        credential = AzureKeyCredential(settings.AZURE_SEARCH_KEY)
        client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_INDEX_NAME,
            credential=credential
        )
        
        resultados = list(client.search(
            search_text=query,
            search_fields=["platos/nombre"],
            filter=" and ".join(filtros) if filtros else None,
            order_by=["max_promocion desc"],
            select=["id", "restaurante", "direccion", "platos", "tipo_menu"]
        ))
    
    # Filtrar platos que coinciden localmente
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
        form = {
            'nombre_cliente': request.POST.get('nombre_cliente'),
            'fecha': request.POST.get('fecha'),
            'hora': request.POST.get('hora')
        }
        
        # Validar formato fecha/hora
        try:
            nueva_reserva = {
                'nombre_cliente': form['nombre_cliente'],
                'fecha': datetime.strptime(form['fecha'], '%Y-%m-%d').strftime('%Y-%m-%d'),
                'hora': datetime.strptime(form['hora'], '%H:%M').strftime('%H:%M')
            }
        except ValueError:
            return render(request, 'reservar.html', {
                'error': 'Formato de fecha/hora inválido',
                'restaurante': restaurante
            })
        
        # Verificar disponibilidad y guardar
        if any(r['fecha'] == nueva_reserva['fecha'] and r['hora'] == nueva_reserva['hora'] 
               for r in restaurante.get('reservas', [])):
            return render(request, 'reservar.html', {
                'error': 'Horario no disponible',
                'restaurante': restaurante
            })
        
        restaurantes.update_one(
            {'_id': ObjectId(restaurante_id)},
            {'$push': {'reservas': nueva_reserva}}
        )
        return redirect('home')
    
    return render(request, 'reservar.html', {'restaurante': restaurante})

# En views.py
def filtrar_restaurantes(request):
    tipologia = request.GET.get('tipologia')
    tipo_menu = request.GET.get('tipo_menu')
    
    query = {}
    if tipologia:
        query['tipologia'] = tipologia
    if tipo_menu:
        query['tipo_menu'] = tipo_menu
    
    resultados = list(restaurantes.find(query))
    return render(request, 'la_cuchara_app/filtrar.html', {'resultados': resultados})

def valorar_plato(request, restaurante_id, plato_nombre):
    if request.method == 'POST':
        try:
            puntuacion = int(request.POST.get('puntuacion'))
            
            # Guardar en SQL (Django)
            Valoracion.objects.create(
                plato_id=f"{restaurante_id}_{plato_nombre}",
                usuario=request.user.username if request.user.is_authenticated else 'Anónimo',
                puntuacion=puntuacion
            )
            
            # Actualizar promedio en MongoDB
            valoraciones = Valoracion.objects.filter(plato_id=f"{restaurante_id}_{plato_nombre}")
            promedio = valoraciones.aggregate(models.Avg('puntuacion'))['puntuacion__avg']
            
            restaurantes.update_one(
                {'_id': ObjectId(restaurante_id), 'platos.nombre': plato_nombre},
                {'$set': {'platos.$.valoracion': round(promedio, 1)}}
            )
            
            # Sincronizar con Azure
            #sync_data()
            
            return redirect('buscar')
        
        except Exception as e:
            print(f"Error al valorar: {str(e)}")
    
    return render(request, 'valorar.html')