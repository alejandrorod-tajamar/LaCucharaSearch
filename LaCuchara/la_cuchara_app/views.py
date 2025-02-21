from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("<h1>Bienvenido a La Cuchara</h1><p>Esta es la página principal.</p>")
