from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser
from .redis_utils import get_confirmation_code
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class OauthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        return token


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    pass


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        try:
            CustomUser.objects.get(email=email)
        except:
            return email
        raise ValidationError('User уже существует!')


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('User не существует!')

        stored_code = get_confirmation_code(user_id)
        if not stored_code:
            raise ValidationError('Код подтверждения не найден или истек!')

        if stored_code != code:
            raise ValidationError('Неверный код подтверждения!')

        return attrs