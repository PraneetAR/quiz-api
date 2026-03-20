from django.contrib import admin
from .models import TopicMastery


@admin.register(TopicMastery)
class TopicMasteryAdmin(admin.ModelAdmin):
    list_display    = ("user", "topic", "mastery_score", "attempts_count", "is_weak_topic", "updated_at")
    list_filter     = ("is_weak_topic",)
    search_fields   = ("user__username", "topic")
    readonly_fields = ("user", "topic", "mastery_score", "total_score", "attempts_count", "is_weak_topic")
    ordering        = ("-mastery_score",)