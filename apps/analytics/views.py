from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import (
    PerformanceDashboardSerializer,
    TopicMasterySerializer,
    TrendSerializer,
    LeaderboardSerializer,
)
from .services import (
    get_performance_dashboard,
    get_topic_mastery,
    get_performance_trend,
    get_leaderboard,
    get_weak_topics,
)
from apps.core.exceptions import ServiceError


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get personal performance dashboard")
    def get(self, request):
        try:
            profile    = get_performance_dashboard(request.user)
            serializer = PerformanceDashboardSerializer(profile)
            return Response({
                "status": "success",
                "data":   serializer.data
            })
        except ServiceError as e:
            return Response({
                "status":  "error",
                "message": e.message
            }, status=status.HTTP_404_NOT_FOUND)


class TopicMasteryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get topic-wise mastery scores")
    def get(self, request):
        masteries  = get_topic_mastery(request.user)
        serializer = TopicMasterySerializer(masteries, many=True)
        return Response({
            "status": "success",
            "data":   serializer.data
        })


class PerformanceTrendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get performance improvement trend")
    def get(self, request):
        trend      = get_performance_trend(request.user)
        serializer = TrendSerializer(trend, many=True)
        return Response({
            "status": "success",
            "data":   serializer.data
        })


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get leaderboard for a topic")
    def get(self, request, topic):
        leaderboard = get_leaderboard(topic)
        serializer  = LeaderboardSerializer(leaderboard, many=True)
        return Response({
            "status": "success",
            "topic":  topic,
            "data":   serializer.data
        })


class WeakTopicsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get topics where user is struggling")
    def get(self, request):
        weak = get_weak_topics(request.user)
        return Response({
            "status":  "success",
            "message": f"{len(weak)} weak topic(s) found.",
            "data":    weak
        })