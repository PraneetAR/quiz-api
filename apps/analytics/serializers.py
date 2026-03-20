from rest_framework import serializers
from .models import TopicMastery
from apps.users.models import UserPerformanceProfile


class TopicMasterySerializer(serializers.ModelSerializer):
    class Meta:
        model  = TopicMastery
        fields = (
            "id", "topic", "attempts_count",
            "mastery_score", "is_weak_topic", "updated_at"
        )


class PerformanceDashboardSerializer(serializers.ModelSerializer):
    username       = serializers.CharField(source="user.username", read_only=True)
    weak_topics    = serializers.SerializerMethodField()

    class Meta:
        model  = UserPerformanceProfile
        fields = (
            "username", "total_attempts", "average_score",
            "best_topic", "weak_topic", "current_streak",
            "weak_topics"
        )

    def get_weak_topics(self, obj):
        weak = TopicMastery.objects.filter(
            user          = obj.user,
            is_weak_topic = True
        ).values_list("topic", flat=True)
        return list(weak)


class TrendSerializer(serializers.Serializer):
    date         = serializers.DateField()
    score        = serializers.FloatField()
    quiz_title   = serializers.CharField()
    topic        = serializers.CharField()


class LeaderboardSerializer(serializers.Serializer):
    username      = serializers.CharField()
    mastery_score = serializers.FloatField()
    attempts      = serializers.IntegerField()