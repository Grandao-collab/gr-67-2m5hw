from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ["phone_number"]
    USERNAME_FIELD = "email"

    def clean(self):
        super().clean()
        if self.phone_number:
            normalized = CustomUser.objects.normalize_phone_number(self.phone_number)
            self.phone_number = normalized

        if self.is_superuser and not self.phone_number:
            raise ValidationError({"phone_number": "Superuser must have a valid phone number"})

        if self.phone_number and not self.phone_number.startswith("+996"):
            raise ValidationError({"phone_number": "Phone number must start with 996"})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email or ""


class ConfirmationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='confirmation_code')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Код подтверждения для {self.user.email}"