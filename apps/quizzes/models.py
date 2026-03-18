from django.db import models
from apps.core.models import BaseModel
from apps.users.models import CustomUser


class QuizTemplate(BaseModel):

    DIFFICULTY_CHOICES = [
        ("easy",   "Easy"),
        ("medium", "Medium"),
        ("hard",   "Hard"),
    ]

    STATUS_CHOICES = [
        ("pending",    "Pending"),
        ("generating", "Generating"),
        ("ready",      "Ready"),
        ("failed",     "Failed"),
    ]

    created_by      = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="quizzes"
    )
    title           = models.CharField(max_length=200)
    topic           = models.CharField(max_length=100)
    difficulty      = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default="medium"
    )
    question_count  = models.PositiveIntegerField(default=5)
    status          = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="pending"
    )
    generation_task_id = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )
    total_attempts  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["topic", "difficulty"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.title} [{self.difficulty}]"


class Question(BaseModel):

    quiz     = models.ForeignKey(
        QuizTemplate,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text          = models.TextField()
    explanation   = models.TextField(blank=True, default="")
    order         = models.PositiveIntegerField(default=0)
    difficulty_weight = models.FloatField(default=1.0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Option(BaseModel):

    question    = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options"
    )
    text        = models.CharField(max_length=500)
    is_correct  = models.BooleanField(default=False)

    def __str__(self):
        marker = "✓" if self.is_correct else "✗"
        return f"{marker} {self.text[:50]}"