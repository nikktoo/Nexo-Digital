from django.contrib import admin
from .models import ContactMessage, UserProfile, Producto, Pedido, DetallePedido

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'created_at', 'read')
    list_filter = ('created_at', 'read')
    search_fields = ('full_name', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'destacado')
    list_editable = ('destacado',)
    list_filter = ('categoria', 'destacado')
    search_fields = ('nombre', 'categoria', 'descripcion')


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'nombre_producto', 'cantidad', 'precio_unitario')
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'usuario', 'metodo_entrega', 'total', 'creado_en')
    list_filter = ('metodo_entrega', 'creado_en')
    search_fields = ('nombre_cliente', 'email_cliente', 'usuario__username')
    readonly_fields = ('usuario', 'nombre_cliente', 'email_cliente', 'metodo_entrega', 'total', 'creado_en')
    inlines = [DetallePedidoInline]