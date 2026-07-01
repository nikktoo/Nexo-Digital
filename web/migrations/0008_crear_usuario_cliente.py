from django.db import migrations
from django.contrib.auth.hashers import make_password

CLIENT_EMAIL = 'cliente@nexodigital.com'
CLIENT_PASSWORD = '12345678'


def crear_cliente(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('web', 'UserProfile')

    user = User.objects.filter(email=CLIENT_EMAIL).first()

    if user is None:
        user = User.objects.create(
            username='cliente_nexo',
            email=CLIENT_EMAIL,
            first_name='Cliente',
            is_staff=False,
            is_superuser=False,
            password=make_password(CLIENT_PASSWORD),
        )
    else:
        # Ya existía, actualizar contraseña
        user.password = make_password(CLIENT_PASSWORD)
        user.save()

    UserProfile.objects.update_or_create(user=user, defaults={'role': 'client'})


def eliminar_cliente(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(email=CLIENT_EMAIL, username='cliente_nexo').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('web', '0007_producto_destacado'),
    ]

    operations = [
        migrations.RunPython(crear_cliente, eliminar_cliente),
    ]
