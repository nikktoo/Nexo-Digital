from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
import json
from .models import Producto, UserProfile, ContactMessage, Pedido, DetallePedido
from .forms import ProductoForm


def auth_view(request):
    if request.user.is_authenticated:
        if es_admin_web(request.user):
            return redirect('web:admin')
        return redirect('web:index')

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'login')

        if form_type == 'login':
            return login_view(request)
        elif form_type == 'register':
            return register_view(request)

    return render(request, 'web/auth.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)

            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, f'¡Bienvenido {user_auth.first_name or user_auth.username}!')
                if es_admin_web(user_auth):
                    return redirect('web:admin')
                return redirect('web:index')
            else:
                messages.error(request, 'Correo o contraseña incorrectos')
        except User.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos')

    return render(request, 'web/auth.html')

def register_view(request):
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
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('web:index')

def index(request):
    productos_destacados = Producto.objects.filter(destacado=True).order_by('-id')[:6]
    if not productos_destacados:
        # Si nadie ha marcado productos como destacados todavía, mostramos los primeros igual
        productos_destacados = Producto.objects.all().order_by('id')[:6]
    productos_recientes = Producto.objects.all().order_by('-id')[:8]
    return render(request, 'web/index.html', {
        'productos_destacados': productos_destacados,
        'productos_recientes': productos_recientes,
    })

def productos(request):
    productos = Producto.objects.all().order_by('nombre')
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    return render(request, 'web/productos.html', {'productos': productos, 'categorias': categorias})

def mision(request):
    return render(request, 'web/mision.html')

def pago(request):
    return render(request, 'web/pago.html')

@require_POST
def procesar_compra(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'Datos inválidos.'}, status=400)

    items = data.get('items', [])
    if not items:
        return JsonResponse({'success': False, 'error': 'El carrito está vacío.'}, status=400)

    # Validar cada ítem enviado desde el carrito antes de crear el pedido.
    # De esta forma protegemos el stock y evitamos compras con datos inválidos.
    errores_stock = []
    productos_a_comprar = []

    try:
        with transaction.atomic():
            for item in items:
                cantidad_raw = item.get('quantity', 0)
                try:
                    cantidad = int(cantidad_raw)
                except (TypeError, ValueError):
                    cantidad = 0
                if cantidad <= 0:
                    continue

                producto_id_raw = item.get('id')
                try:
                    producto_id = int(producto_id_raw)
                except (TypeError, ValueError):
                    # Esto pasaba cuando el carrito mandaba ids como "prod5" en vez de 5
                    errores_stock.append({'id': producto_id_raw, 'nombre': f'Producto inválido ({producto_id_raw})', 'disponible': 0})
                    continue

                # select_for_update bloquea la fila hasta que termine la transacción,
                # evitando que dos compras simultáneas dejen el stock en negativo.
                try:
                    producto = Producto.objects.select_for_update().get(id=producto_id)
                except Producto.DoesNotExist:
                    errores_stock.append({'id': producto_id, 'nombre': 'Producto no encontrado', 'disponible': 0})
                    continue

                if producto.stock < cantidad:
                    errores_stock.append({'id': producto.id, 'nombre': producto.nombre, 'disponible': producto.stock})
                else:
                    productos_a_comprar.append((producto, cantidad))

            if errores_stock:
                raise ValueError('stock_insuficiente')

            if not productos_a_comprar:
                return JsonResponse({'success': False, 'error': 'No se encontraron productos válidos en el carrito.'}, status=400)

            total = 0
            pedido = Pedido.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                nombre_cliente=str(data.get('nombre', '')).strip(),
                email_cliente=str(data.get('email', '')).strip(),
                metodo_entrega=data.get('metodo_entrega', 'delivery'),
            )

            for producto, cantidad in productos_a_comprar:
                producto.stock -= cantidad
                producto.save(update_fields=['stock'])

                subtotal = producto.precio * cantidad
                total += subtotal

                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    nombre_producto=producto.nombre,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )

            pedido.total = total
            pedido.save(update_fields=['total'])

    except ValueError as e:
        if str(e) == 'stock_insuficiente':
            return JsonResponse({
                'success': False,
                'error': 'No hay stock suficiente para uno o más productos.',
                'stock_insuficiente': errores_stock,
            }, status=409)
        raise

    return JsonResponse({'success': True, 'pedido_id': pedido.id, 'total': float(total)})

def envios(request):
    return render(request, 'web/envios.html')

def garantia(request):
    return render(request, 'web/garantia.html')

def contacto(request):
    return render(request, 'web/contacto.html')

def es_admin_web(user):
    if user.is_staff or user.is_superuser:
        return True
    try:
        return user.profile.role == 'admin'
    except UserProfile.DoesNotExist:
        return False


@login_required(login_url='web:auth')
def admin(request):
    """Panel administrador propio del sitio."""
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para acceder al panel de administración')
        return redirect('web:index')

    productos = Producto.objects.all().order_by('nombre')
    usuarios = User.objects.all().order_by('-date_joined')
    for usuario in usuarios:
        UserProfile.objects.get_or_create(user=usuario)
    mensajes = ContactMessage.objects.all()

    total_productos = productos.count()
    total_usuarios = User.objects.count()
    total_mensajes = mensajes.count()
    total_mensajes_no_leidos = mensajes.filter(read=False).count()
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().count()
    total_stock = sum(p.stock for p in productos)
    productos_sin_stock = productos.filter(stock=0).count()
    productos_bajo_stock = productos.filter(stock__gt=0, stock__lte=5)

    context = {
        'productos': productos,
        'usuarios': usuarios,
        'mensajes': mensajes,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'total_mensajes': total_mensajes,
        'total_mensajes_no_leidos': total_mensajes_no_leidos,
        'categorias': categorias,
        'total_stock': total_stock,
        'productos_sin_stock': productos_sin_stock,
        'productos_bajo_stock': productos_bajo_stock,
        'roles': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'web/admin.html', context)


@login_required(login_url='web:auth')
def admin_producto_crear(request):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente')
            return redirect('web:admin')
    else:
        form = ProductoForm()

    return render(request, 'web/admin_producto_form.html', {
        'form': form,
        'titulo': 'Agregar producto',
        'boton': 'Guardar producto',
    })


@login_required(login_url='web:auth')
def admin_producto_editar(request, producto_id):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')

    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente')
            return redirect('web:admin')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'web/admin_producto_form.html', {
        'form': form,
        'titulo': 'Editar producto',
        'boton': 'Actualizar producto',
        'producto': producto,
    })


@login_required(login_url='web:auth')
def admin_producto_eliminar(request, producto_id):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')

    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente')
        return redirect('web:admin')

    return render(request, 'web/admin_producto_confirmar_eliminar.html', {'producto': producto})

def buscar_productos_ajax(request):
    query = request.GET.get('q', '')
    resultados = []
    if query:
        productos = Producto.objects.filter(nombre__icontains=query)[:5]
        for p in productos:
            resultados.append({
                'id': p.id,
                'nombre': p.nombre,
                'precio': str(p.precio),
                'stock': p.stock,
                'url': f'/producto/{p.id}/'
            })
    return JsonResponse({'productos': resultados})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, "web/detalle_producto.html", {"producto": producto})


@login_required(login_url='web:auth')
@require_POST
def admin_mensaje_marcar_leido(request, mensaje_id):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')
    mensaje = get_object_or_404(ContactMessage, id=mensaje_id)
    mensaje.read = True
    mensaje.save()
    messages.success(request, 'Mensaje marcado como leído')
    return redirect('web:admin')


@login_required(login_url='web:auth')
@require_POST
def admin_mensaje_eliminar(request, mensaje_id):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')
    mensaje = get_object_or_404(ContactMessage, id=mensaje_id)
    mensaje.delete()
    messages.success(request, 'Mensaje eliminado correctamente')
    return redirect('web:admin')


@login_required(login_url='web:auth')
@require_POST
def admin_usuario_cambiar_rol(request, user_id):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')

    usuario = get_object_or_404(User, id=user_id)
    nuevo_rol = request.POST.get('role', 'client')
    roles_validos = [rol[0] for rol in UserProfile.ROLE_CHOICES]

    if nuevo_rol not in roles_validos:
        messages.error(request, 'Rol no válido')
        return redirect('web:admin')

    perfil, _ = UserProfile.objects.get_or_create(user=usuario)
    perfil.role = nuevo_rol
    perfil.save()

    usuario.is_staff = nuevo_rol == 'admin'
    usuario.save()

    messages.success(request, 'Rol de usuario actualizado correctamente')
    return redirect('web:admin')


@login_required(login_url='web:auth')
@require_POST
def admin_usuario_eliminar(request, user_id):
    if not es_admin_web(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('web:index')

    usuario = get_object_or_404(User, id=user_id)

    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propio usuario desde el panel')
        return redirect('web:admin')

    nombre_usuario = usuario.username
    usuario.delete()
    messages.success(request, f'Usuario {nombre_usuario} eliminado correctamente')
    return redirect('web:admin')