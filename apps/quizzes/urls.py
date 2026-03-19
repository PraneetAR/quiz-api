from django.urls import path
from .views import (
    QuizGenerateView,
    QuizListView,
    QuizDetailView,
    MyQuizzesView,
)

urlpatterns = [
    path("generate/",      QuizGenerateView.as_view(), name="quiz-generate"),
    path("",               QuizListView.as_view(),     name="quiz-list"),
    path("<uuid:quiz_id>/", QuizDetailView.as_view(),  name="quiz-detail"),
    path("mine/",          MyQuizzesView.as_view(),    name="quiz-mine"),
]

