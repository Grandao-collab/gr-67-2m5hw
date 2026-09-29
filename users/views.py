from typing import Any, cast

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView

from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationSerializer,
    CustomTokenObtainPairSerializer,
)
from .models import ConfirmationCode, CustomUser
import random
import string
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer

    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data or {})
        user = authenticate(**validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={'error': 'User account is not activated yet!'}
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={'key': token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={'error': 'User credentials are wrong!'}
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data or {})
        email = validated_data.get('email')
        password = validated_data.get('password')

        # Use transaction to ensure data consistency
        birthdate = validated_data.get('birthdate')

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                birthdate=birthdate,
                is_active=False
            )

            # Create a random 6-digit code
            code = ''.join(random.choices(string.digits, k=6))

            confirmation_code = ConfirmationCode.objects.create(
                user=user,
                code=code
            )

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'user_id': user.id,
                'confirmation_code': code
            }
        )


class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data or {})
        user_id = validated_data.get('user_id')

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            ConfirmationCode.objects.filter(user=user).delete()

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'User аккаунт успешно активирован',
                'key': token.key
            }
        )