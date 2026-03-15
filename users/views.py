from django.contrib.auth import authenticate
from django.db.migrations import serializer
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": serializer.data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = authenticate(username=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        data = request.data

        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if current_password or new_password:
            if not current_password:
                return Response(
                    {"details": "Please provide your current password."},
                    status=status.HTTP_400_BAD_REQUEST)

            if not new_password:
                return Response({"detail": "Please provide a new password."}, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_password:
                return Response({"detail": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(current_password):
                return Response({"detail": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

        profile_data = {
            "name": data.get("name", user.name),
            "last_name": data.get("last_name", user.last_name),
            "email": data.get("email", user.email),
        }

        serializer = UserSerializer(request.user, data=profile_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "detail": "Profile updated successfully!",
                "user": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as e:
            # Expired or invalid tokens
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_400_BAD_REQUEST,
            )
