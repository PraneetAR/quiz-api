from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import BaseModel


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin",   "Admin"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="student"
    )
    bio = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_teacher(self):
        return self.role == "teacher"

    @property
    def is_admin_user(self):
        return self.role == "admin"


class UserPerformanceProfile(BaseModel):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="performance"
    )
    total_attempts   = models.PositiveIntegerField(default=0)
    total_score      = models.FloatField(default=0.0)
    average_score    = models.FloatField(default=0.0)
    best_topic       = models.CharField(max_length=100, blank=True, default="")
    weak_topic       = models.CharField(max_length=100, blank=True, default="")
    current_streak   = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - avg: {self.average_score:.1f}%"

    def update_after_attempt(self, score: float):
        self.total_attempts += 1
        self.total_score    += score
        self.average_score   = self.total_score / self.total_attempts
        self.save(update_fields=[
            "total_attempts", "total_score",
            "average_score", "updated_at"
        ])