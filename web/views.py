from django.shortcuts import render

def index(request):
    return render(request, 'web/index.html')

def productos(request):
    return render(request, 'web/productos.html')

def oferta(request):
    return render(request, 'web/oferta.html')

def login(request):
    return render(request, 'web/login.html')

def pago(request):
    return render(request, 'web/pago.html')

def envios(request):
    return render(request, 'web/envios.html')

def garantia(request):
    return render(request, 'web/garantia.html')

def admin(request):
    return render(request, 'web/admin.html')
