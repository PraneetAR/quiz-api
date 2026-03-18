from django.contrib import admin
from .models import QuizSession, QuestionResponse


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display  = ("user", "quiz", "status", "score", "correct_count", "created_at")
    list_filter   = ("status",)
    search_fields = ("user__username", "quiz__title")


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "is_correct", "time_taken_seconds")