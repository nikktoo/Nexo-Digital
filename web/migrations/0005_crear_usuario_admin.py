from django.db import migrations
from django.contrib.auth.hashers import make_password

ADMIN_EMAIL = 'Admin@gmail.com'
ADMIN_PASSWORD = '1029384756'


def crear_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('web', 'UserProfile')

    user = User.objects.filter(email=ADMIN_EMAIL).first()

    if user is None:
        user = User.objects.create(
            username='admin_nexo',
            email=ADMIN_EMAIL,
            first_name='Administrador',
            is_staff=True,
            is_superuser=True,
            password=make_password(ADMIN_PASSWORD),
        )
    else:
        # Ya existía (por ejemplo, te registraste con ese correo desde el sitio).
        # Lo ascendemos a administrador y dejamos la contraseña documentada.
        user.is_staff = True
        user.is_superuser = True
        user.password = make_password(ADMIN_PASSWORD)
        user.save()

    UserProfile.objects.update_or_create(user=user, defaults={'role': 'admin'})


def eliminar_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(email=ADMIN_EMAIL, username='admin_nexo').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('web', '0004_cargar_productos_iniciales'),
    ]

    operations = [
        migrations.RunPython(crear_admin, eliminar_admin),
    ]
