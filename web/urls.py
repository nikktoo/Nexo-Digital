from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.auth_view, name='auth'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register_view, name='register_view'),
    path('logout/', views.logout_view, name='logout'),
    path('inicio/', views.index, name='index'),
    path('productos/', views.productos, name='productos'),
    path('mision/', views.mision, name='mision'),
    path('pago/', views.pago, name='pago'),
    path('envios/', views.envios, name='envios'),
    path('contacto/', views.contacto, name='contacto'),
    path('garantia/', views.garantia, name='garantia'),
    path('admin/', views.admin, name='admin'),
]

