import re

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    @staticmethod
    def normalize_phone_number(phone_number):
        if phone_number is None:
            return ""

        cleaned = str(phone_number).strip()
        if not cleaned:
            return ""

        digits = re.sub(r"\D", "", cleaned)
        if digits.startswith("996"):
            return f"+{digits}"

        raise ValueError("Phone number must start with 996")

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        phone_number = extra_fields.get("phone_number")
        if phone_number:
            extra_fields["phone_number"] = self.normalize_phone_number(phone_number)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be have is_staff=True")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must be have is_active=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be have is_superuser=True")

        phone_number = extra_fields.get("phone_number")
        if not phone_number:
            raise ValueError("Superuser must have a valid phone number")

        extra_fields["phone_number"] = self.normalize_phone_number(phone_number)
        return self.create_user(email, password, **extra_fields)
