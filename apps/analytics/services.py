from django.db.models import Avg, Count
from .models import TopicMastery
from apps.attempts.models import QuizSession
from apps.users.models import UserPerformanceProfile
from apps.core.exceptions import ServiceError


def get_performance_dashboard(user) -> UserPerformanceProfile:

    try:
        profile = user.performance
    except UserPerformanceProfile.DoesNotExist:
        raise ServiceError("Performance profile not found.", code="not_found")

    topic_scores = TopicMastery.objects.filter(user=user).order_by("-mastery_score")

    if topic_scores.exists():
        profile.best_topic = topic_scores.first().topic
        profile.weak_topic = topic_scores.last().topic
        profile.save(update_fields=["best_topic", "weak_topic", "updated_at"])

    return profile


def get_topic_mastery(user) -> list:

    return TopicMastery.objects.filter(
        user=user
    ).order_by("-mastery_score")


def get_performance_trend(user) -> list:

    sessions = QuizSession.objects.filter(
        user   = user,
        status = "completed"
    ).select_related("quiz").order_by("completed_at")[:20]

    trend = []
    for session in sessions:
        trend.append({
            "date":       session.completed_at.date(),
            "score":      session.percentage_score,
            "quiz_title": session.quiz.title,
            "topic":      session.quiz.topic,
        })

    return trend


def get_leaderboard(topic: str) -> list:

    masteries = TopicMastery.objects.filter(
        topic = topic
    ).select_related("user").order_by("-mastery_score")[:10]

    leaderboard = []
    for mastery in masteries:
        leaderboard.append({
            "username":      mastery.user.username,
            "mastery_score": round(mastery.mastery_score, 2),
            "attempts":      mastery.attempts_count,
        })

    return leaderboard


def get_weak_topics(user) -> list:

    return list(
        TopicMastery.objects.filter(
            user          = user,
            is_weak_topic = True
        ).values("topic", "mastery_score", "attempts_count")
    )