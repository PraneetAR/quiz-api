from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserPerformanceProfile


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model  = CustomUser
        fields = (
            "id", "username", "email",
            "password", "password_confirm",
            "role", "first_name", "last_name"
        )
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):

    average_score  = serializers.FloatField(
        source="performance.average_score",
        read_only=True
    )
    total_attempts = serializers.IntegerField(
        source="performance.total_attempts",
        read_only=True
    )

    class Meta:
        model  = CustomUser
        fields = (
            "id", "username", "email", "role",
            "first_name", "last_name", "bio",
            "average_score", "total_attempts",
            "date_joined"
        )
        read_only_fields = ("id", "role", "date_joined")


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )