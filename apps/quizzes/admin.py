from django.contrib import admin
from .models import QuizTemplate, Question, Option


class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 0


class OptionInline(admin.TabularInline):
    model  = Option
    extra  = 0


@admin.register(QuizTemplate)
class QuizTemplateAdmin(admin.ModelAdmin):
    list_display  = ("title", "topic", "difficulty", "status", "total_attempts", "created_at")
    list_filter   = ("difficulty", "status")
    search_fields = ("title", "topic")
    inlines       = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order", "difficulty_weight")
    inlines      = [OptionInline]