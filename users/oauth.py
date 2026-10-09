import os

import requests
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.serializers import OauthCodeSerializer


class GoogleLoginAPIView(CreateAPIView):
    serializer_class = OauthCodeSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get("code")

        token_response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
                "grant_type": "authorization_code",
            },
        )
        token = token_response.json()
        access_token = token.get("access_token")

        print("access_token", access_token)

        if not access_token:
            return Response(
                {"error": "Invalid access_token!"}, status=status.HTTP_418_IM_A_TEAPOT
            )

        user_info = requests.get(
            url="https://www.googleapis.com/oauth2/v3/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        print("user_info", user_info)

        email = user_info["email"]
        first_name = (user_info.get("given_name") or "").strip()
        last_name = (user_info.get("family_name") or "").strip()

        user, _ = CustomUser.objects.get_or_create(email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.registration_source = "google"
        user.is_active = True
        user.last_login = timezone.now()
        user.save(update_fields=["first_name", "last_name", "registration_source", "is_active", "last_login"])

        refresh = RefreshToken.for_user(user)
        refresh["email"] = email
        refresh["is_staff"] = user.is_staff

        return Response(
            {"access_token": str(refresh.access_token), "refresh_token": str(refresh)},
            status=status.HTTP_200_OK,
        )
