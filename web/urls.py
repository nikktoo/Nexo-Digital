from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('productos/', views.productos, name='productos'),
    path('oferta/', views.oferta, name='oferta'),
    path('login/', views.login, name='login'),
    path('pago/', views.pago, name='pago'),
    path('envios/', views.envios, name='envios'),
    path('garantia/', views.garantia, name='garantia'),
    path('admin/', views.admin, name='admin'),
]
