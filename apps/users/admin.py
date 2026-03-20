from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPerformanceProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display    = ("username", "email", "role", "is_active", "date_joined")
    list_filter     = ("role", "is_active")
    search_fields   = ("username", "email")
    ordering        = ("-date_joined",)
    fieldsets       = UserAdmin.fieldsets + (
        ("Role & Profile", {"fields": ("role", "bio")}),
    )
    actions         = ["deactivate_users", "activate_users"]

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} user(s) deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} user(s) activated.")
    activate_users.short_description = "Activate selected users"


@admin.register(UserPerformanceProfile)
class UserPerformanceProfileAdmin(admin.ModelAdmin):
    list_display    = ("user", "total_attempts", "average_score", "best_topic", "weak_topic", "current_streak")
    search_fields   = ("user__username",)
    readonly_fields = ("user", "total_attempts", "total_score", "average_score", "best_topic", "weak_topic")