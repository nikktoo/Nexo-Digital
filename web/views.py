from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile

def auth_view(request):
    """Handle authentication page with login and registration"""
    if request.user.is_authenticated:
        return redirect('web:index')

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'login')

        if form_type == 'login':
            return login_view(request)
        elif form_type == 'register':
            return register_view(request)

    return render(request, 'web/auth.html')

def login_view(request):
    """Process login form submission"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)

            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, f'¡Bienvenido {user_auth.first_name or user_auth.username}!')
                return redirect('web:index')
            else:
                messages.error(request, 'Correo o contraseña incorrectos')
        except User.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos')

    return render(request, 'web/auth.html')

def register_view(request):
    """Process registration form submission"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'web/auth.html')

        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return render(request, 'web/auth.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado')
            return render(request, 'web/auth.html')

        try:
            username = email.split('@')[0]
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.count()}"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name
            )

            UserProfile.objects.create(user=user, role='client')

            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido {full_name}')
                return redirect('web:index')
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Intenta de nuevo.')

    return render(request, 'web/auth.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('web:auth')

@login_required(login_url='web:auth')
def index(request):
    """Home page - requires authentication"""
    return render(request, 'web/index.html')

@login_required(login_url='web:auth')
def productos(request):
    """Products page - requires authentication"""
    return render(request, 'web/productos.html')

@login_required(login_url='web:auth')
def oferta(request):
    """Offers page - requires authentication"""
    return render(request, 'web/oferta.html')

@login_required(login_url='web:auth')
def pago(request):
    """Payment page - requires authentication"""
    return render(request, 'web/pago.html')

@login_required(login_url='web:auth')
def envios(request):
    """Shipping information page - requires authentication"""
    return render(request, 'web/envios.html')

@login_required(login_url='web:auth')
def garantia(request):
    """Warranty and returns page - requires authentication"""
    return render(request, 'web/garantia.html')

@login_required(login_url='web:auth')
def admin(request):
    """Admin panel - requires authentication and admin privileges"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder al panel de administración')
        return redirect('web:index')
    return render(request, 'web/admin.html')
