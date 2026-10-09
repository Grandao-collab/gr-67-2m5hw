from django.contrib import admin

# Register your models here.
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["id", "email", "first_name", "last_name", "registration_source", "is_active"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password", "is_active", "registration_source")}),
        ("Personal info", {"fields": ("first_name", "last_name", "last_login", "is_superuser")}),
    )
