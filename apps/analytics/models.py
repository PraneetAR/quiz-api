from django.db import models
from apps.core.models import BaseModel
from apps.users.models import CustomUser


class TopicMastery(BaseModel):

    user            = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="topic_masteries"
    )
    topic           = models.CharField(max_length=100)
    attempts_count  = models.PositiveIntegerField(default=0)
    total_score     = models.FloatField(default=0.0)
    mastery_score   = models.FloatField(default=0.0)
    is_weak_topic   = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "topic")
        ordering = ["-mastery_score"]
        indexes = [
            models.Index(fields=["user", "topic"]),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.topic}: {self.mastery_score:.1f}%"

    def update_mastery(self, new_score: float):
        self.attempts_count += 1
        self.total_score    += new_score
        self.mastery_score   = self.total_score / self.attempts_count
        self.is_weak_topic   = self.mastery_score < 40.0
        self.save(update_fields=[
            "attempts_count", "total_score",
            "mastery_score", "is_weak_topic", "updated_at"
        ])