from django.db import models
from apps.core.models import BaseModel


class AIGenerationLog(BaseModel):

    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed",  "Failed"),
        ("retried", "Retried"),
    ]

    quiz_template_id    = models.UUIDField(null=True, blank=True)
    prompt_used         = models.TextField()
    raw_response        = models.TextField(blank=True, default="")
    status              = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="success"
    )
    latency_ms          = models.PositiveIntegerField(default=0)
    retry_count         = models.PositiveIntegerField(default=0)
    error_message       = models.TextField(blank=True, default="")
    tokens_used         = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AILog [{self.status}] {self.created_at:%Y-%m-%d %H:%M}"