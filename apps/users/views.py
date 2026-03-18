from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import UserProfileSerializer, ChangePasswordSerializer
from .services import register_user, login_user, logout_user, change_password
from apps.core.exceptions import ServiceError


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Register a new user")
    def post(self, request):
        try:
            data = register_user(request.data)
            return Response({
                "status":  "success",
                "message": "Account created successfully.",
                "data":    data
            }, status=status.HTTP_201_CREATED)
        except ServiceError as e:
            return Response({
                "status":  "error",
                "code":    e.code,
                "message": e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Login and get JWT tokens")
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({
                "status":  "error",
                "message": "Username and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = login_user(username, password)
            return Response({
                "status":  "success",
                "message": "Login successful.",
                "data":    data
            }, status=status.HTTP_200_OK)
        except ServiceError as e:
            return Response({
                "status":  "error",
                "code":    e.code,
                "message": e.message
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Logout and blacklist refresh token")
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({
                "status":  "error",
                "message": "Refresh token is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            logout_user(refresh_token)
            return Response({
                "status":  "success",
                "message": "Logged out successfully."
            }, status=status.HTTP_200_OK)
        except ServiceError as e:
            return Response({
                "status":  "error",
                "code":    e.code,
                "message": e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get current user profile")
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({
            "status": "success",
            "data":   serializer.data
        })

    @extend_schema(summary="Update current user profile")
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Profile updated.",
                "data":    serializer.data
            })
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Change user password")
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            change_password(
                user=request.user,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"]
            )
            return Response({
                "status":  "success",
                "message": "Password changed successfully."
            })
        except ServiceError as e:
            return Response({
                "status":  "error",
                "message": e.message
            }, status=status.HTTP_400_BAD_REQUEST)