from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import ConfirmationCode, CustomUser


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Email для входа/регистрации")
    password = serializers.CharField(write_only=True, help_text="Пароль пользователя")


class AuthValidateSerializer(UserBaseSerializer):
    """Сериализатор логина: явно описывает поля для Swagger"""
    pass


class RegisterValidateSerializer(serializers.Serializer):
    """Сериализатор регистрации: явные поля для корректной схемы в Swagger"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('User уже существует!')
        return email

    def validate_phone_number(self, value):
        if not value:
            return value
        try:
            return CustomUser.objects.normalize_phone_number(value)
        except ValueError as exc:
            raise ValidationError('Phone number must start with 996') from exc

    def create(self, validated_data):
        password = validated_data.pop('password')
        return CustomUser.objects.create_user(password=password, **validated_data)


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('User не существует!')

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError('Код подтверждения не найден!')

        if confirmation_code.code != code:
            raise ValidationError('Неверный код подтверждения!')

        return attrs