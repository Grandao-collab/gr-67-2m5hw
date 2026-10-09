from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from users.models import CustomUser
from users.redis_utils import consume_confirmation_code, save_confirmation_code


class CustomUserOAuthAndRedisTests(TestCase):
    def test_google_oauth_user_tracks_profile_and_registration_source(self):
        user = CustomUser.objects.create_user(
            email="google-user@example.com",
            password="strong-pass",
            first_name="Jane",
            last_name="Doe",
            registration_source="google",
            is_active=True,
        )
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.registration_source, "google")
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.last_login)

    def test_confirmation_code_is_saved_in_redis_with_ttl_and_removed_after_use(self):
        user = CustomUser.objects.create_user(email="code-user@example.com", password="strong-pass")

        save_confirmation_code(user.id, "123456")
        code = cache.get(f"confirmation_code:{user.id}")

        self.assertEqual(code, "123456")
        self.assertGreaterEqual(cache.ttl(f"confirmation_code:{user.id}"), 1)
        self.assertLessEqual(cache.ttl(f"confirmation_code:{user.id}"), 300)

        self.assertTrue(consume_confirmation_code(user.id, "123456"))
        self.assertIsNone(cache.get(f"confirmation_code:{user.id}"))
