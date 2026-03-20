from django.contrib import admin
from .models import AIGenerationLog


@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display    = ("status", "latency_ms", "retry_count", "tokens_used", "created_at")
    list_filter     = ("status",)
    search_fields   = ("prompt_used", "error_message")
    readonly_fields = (
        "quiz_template_id", "prompt_used", "raw_response",
        "status", "latency_ms", "retry_count",
        "error_message", "tokens_used", "created_at"
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False