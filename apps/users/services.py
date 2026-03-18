from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from apps.core.exceptions import ServiceError


def register_user(validated_data: dict) -> dict:
    """
    Creates a new user and returns JWT tokens immediately.
    User doesn't need to login separately after registration.
    """
    from .serializers import RegisterSerializer

    serializer = RegisterSerializer(data=validated_data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    tokens = _generate_tokens(user)
    return {
        "user": {
            "id":       str(user.id),
            "username": user.username,
            "email":    user.email,
            "role":     user.role,
        },
        "tokens": tokens
    }


def login_user(username: str, password: str) -> dict:
    """
    Authenticates user and returns JWT tokens.
    Raises ServiceError if credentials are wrong.
    """
    user = authenticate(username=username, password=password)

    if user is None:
        raise ServiceError(
            message="Invalid username or password.",
            code="invalid_credentials"
        )

    if not user.is_active:
        raise ServiceError(
            message="This account has been deactivated.",
            code="account_inactive"
        )

    tokens = _generate_tokens(user)
    return {
        "user": {
            "id":       str(user.id),
            "username": user.username,
            "email":    user.email,
            "role":     user.role,
        },
        "tokens": tokens
    }


def logout_user(refresh_token: str) -> None:
    """
    Blacklists the refresh token so it can't be used again.
    Access token expires naturally (short lifetime).
    """
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        raise ServiceError(
            message="Invalid or expired refresh token.",
            code="invalid_token"
        )


def change_password(user: CustomUser, old_password: str, new_password: str) -> None:
    """
    Verifies old password then sets new one.
    """
    if not user.check_password(old_password):
        raise ServiceError(
            message="Old password is incorrect.",
            code="wrong_password"
        )
    user.set_password(new_password)
    user.save(update_fields=["password"])


def _generate_tokens(user: CustomUser) -> dict:
    """
    Private helper — generates access + refresh token pair.
    Underscore prefix means: don't call this from outside this file.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access":  str(refresh.access_token),
        "refresh": str(refresh),
    }