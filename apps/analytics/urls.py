from django.urls import path
from .views import (
    DashboardView,
    TopicMasteryView,
    PerformanceTrendView,
    LeaderboardView,
    WeakTopicsView,
)

urlpatterns = [
    path("me/",                        DashboardView.as_view(),        name="analytics-dashboard"),
    path("me/topics/",                 TopicMasteryView.as_view(),     name="analytics-topics"),
    path("me/trend/",                  PerformanceTrendView.as_view(), name="analytics-trend"),
    path("me/weak/",                   WeakTopicsView.as_view(),       name="analytics-weak"),
    path("leaderboard/<str:topic>/",   LeaderboardView.as_view(),      name="analytics-leaderboard"),
]