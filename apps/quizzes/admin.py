from django.contrib import admin
from .models import QuizTemplate, Question, Option


class OptionInline(admin.TabularInline):
    model   = Option
    extra   = 0
    fields  = ("text", "is_correct", "is_active")


class QuestionInline(admin.TabularInline):
    model   = Question
    extra   = 0
    fields  = ("text", "order", "difficulty_weight", "is_active")
    ordering = ("order",)


@admin.register(QuizTemplate)
class QuizTemplateAdmin(admin.ModelAdmin):
    list_display    = ("title", "topic", "difficulty", "status", "total_attempts", "created_by", "created_at")
    list_filter     = ("difficulty", "status")
    search_fields   = ("title", "topic", "created_by__username")
    readonly_fields = ("status", "generation_task_id", "total_attempts", "created_at", "updated_at")
    inlines         = [QuestionInline]
    actions         = ["mark_as_ready", "mark_as_failed"]

    def mark_as_ready(self, request, queryset):
        queryset.update(status="ready")
        self.message_user(request, f"{queryset.count()} quiz(zes) marked as ready.")
    mark_as_ready.short_description = "Mark selected quizzes as ready"

    def mark_as_failed(self, request, queryset):
        queryset.update(status="failed")
        self.message_user(request, f"{queryset.count()} quiz(zes) marked as failed.")
    mark_as_failed.short_description = "Mark selected quizzes as failed"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display    = ("text", "quiz", "order", "difficulty_weight", "is_active")
    list_filter     = ("quiz__difficulty", "is_active")
    search_fields   = ("text", "quiz__title")
    inlines         = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display    = ("text", "question", "is_correct", "is_active")
    list_filter     = ("is_correct",)
    search_fields   = ("text", "question__text")