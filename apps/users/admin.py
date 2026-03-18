from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPerformanceProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ("username", "email", "role", "is_active", "date_joined")
    list_filter   = ("role", "is_active")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (
        ("Role & Profile", {"fields": ("role", "bio")}),
    )


@admin.register(UserPerformanceProfile)
class UserPerformanceProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "total_attempts", "average_score", "current_streak")
    search_fields = ("user__username",)