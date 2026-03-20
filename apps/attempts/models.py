from django.db import models
from apps.core.models import BaseModel
from apps.users.models import CustomUser
from apps.quizzes.models import QuizTemplate, Question, Option


class QuizSession(BaseModel):

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed",   "Completed"),
        ("abandoned",   "Abandoned"),
    ]

    user       = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    quiz       = models.ForeignKey(
        QuizTemplate,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    status     = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="in_progress"
    )
    score               = models.FloatField(default=0.0)
    total_questions     = models.PositiveIntegerField(default=0)
    correct_count       = models.PositiveIntegerField(default=0)
    time_taken_seconds  = models.PositiveIntegerField(default=0)
    completed_at        = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["quiz", "status"]),
        ]

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.quiz.title} [{self.status}]"

    @property
    def percentage_score(self):
        if self.total_questions == 0:
            return 0.0
        return round((self.correct_count / self.total_questions) * 100, 2)


class QuestionResponse(BaseModel):

    session         = models.ForeignKey(
        QuizSession,
        on_delete=models.CASCADE,
        related_name="responses"
    )
    question        = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="responses"
    )
    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responses"
    )
    is_correct          = models.BooleanField(default=False)
    time_taken_seconds  = models.PositiveIntegerField(default=0)
    explanation_viewed  = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "question")
        indexes         = [
            models.Index(fields=["session", "is_correct"]),
        ]

    def __str__(self):
        result = "✓" if self.is_correct else "✗"
        return f"{result} {self.session.user.username} on Q: {self.question.text[:40]}"