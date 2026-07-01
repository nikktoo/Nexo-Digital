from django.contrib.auth.models import User
from django.test import TestCase

from .models import UserProfile
from .views import es_admin_web, es_cliente_web


class UserRoleTests(TestCase):
    def test_client_user_is_not_admin(self):
        user = User.objects.create_user(
            username='cliente_prueba',
            email='cliente@test.com',
            password='12345678',
        )
        UserProfile.objects.create(user=user, role='client')

        self.assertFalse(es_admin_web(user))
        self.assertTrue(es_cliente_web(user))

    def test_admin_user_is_admin(self):
        user = User.objects.create_user(
            username='admin_prueba',
            email='admin@test.com',
            password='12345678',
        )
        UserProfile.objects.create(user=user, role='admin')

        self.assertTrue(es_admin_web(user))
        self.assertFalse(es_cliente_web(user))
