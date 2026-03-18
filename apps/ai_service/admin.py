from django.contrib import admin
from .models import AIGenerationLog


@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display  = ("status", "latency_ms", "retry_count", "tokens_used", "created_at")
    list_filter   = ("status",)
    readonly_fields = (
        "prompt_used", "raw_response", "status",
        "latency_ms", "retry_count", "error_message", "tokens_used"
    )