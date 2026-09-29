from datetime import date, timedelta
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from common.permissions import IsModerator
from product.models import Category, Product
from product.serializers import ProductValidateSerializer


class ProductAgeValidationTests(TestCase):
    def test_missing_birthdate_fails_for_product_creation(self):
        request = SimpleNamespace(auth={'birthdate': None})
        serializer = ProductValidateSerializer(
            data={'title': 'Laptop', 'description': 'Nice', 'price': 1200.0, 'category': 1},
            context={'request': request},
        )

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_underage_user_fails_for_product_creation(self):
        birthdate = date.today() - timedelta(days=365 * 17 + 364)
        request = SimpleNamespace(auth={'birthdate': birthdate.isoformat()})
        serializer = ProductValidateSerializer(
            data={'title': 'Laptop', 'description': 'Nice', 'price': 1200.0, 'category': 1},
            context={'request': request},
        )

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class ModeratorPermissionTests(TestCase):
    def test_moderator_has_permission_for_non_post_methods(self):
        moderator = get_user_model().objects.create_user(
            email='moderator@example.com',
            password='secret123',
            is_staff=True,
            is_active=True,
        )

        request = SimpleNamespace(user=moderator, method='PATCH', auth={'birthdate': date.today().isoformat()})
        self.assertTrue(IsModerator().has_permission(request, None))

    def test_moderator_cannot_create_products(self):
        moderator = get_user_model().objects.create_user(
            email='mod2@example.com',
            password='secret123',
            is_staff=True,
            is_active=True,
        )

        request = SimpleNamespace(user=moderator, method='POST', auth={'birthdate': date.today().isoformat()})
        self.assertFalse(IsModerator().has_permission(request, None))
