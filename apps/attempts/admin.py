from django.contrib import admin
from .models import QuizSession, QuestionResponse


class QuestionResponseInline(admin.TabularInline):
    model      = QuestionResponse
    extra      = 0
    readonly_fields = ("question", "selected_option", "is_correct", "time_taken_seconds", "explanation_viewed")
    can_delete = False


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display    = ("user", "quiz", "status", "score", "correct_count", "total_questions", "time_taken_seconds", "created_at")
    list_filter     = ("status",)
    search_fields   = ("user__username", "quiz__title")
    readonly_fields = ("user", "quiz", "score", "correct_count", "total_questions", "time_taken_seconds", "completed_at")
    inlines         = [QuestionResponseInline]


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display    = ("session", "question", "is_correct", "time_taken_seconds", "explanation_viewed")
    list_filter     = ("is_correct", "explanation_viewed")
    search_fields   = ("session__user__username", "question__text")
    readonly_fields = ("session", "question", "selected_option", "is_correct")