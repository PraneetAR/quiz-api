from django.urls import path
from .views import (
    StartAttemptView,
    SubmitAnswerView,
    SubmitAttemptView,
    AttemptResultView,
    AttemptHistoryView,
)

urlpatterns = [
    path("start/",                          StartAttemptView.as_view(),   name="attempt-start"),
    path("<uuid:session_id>/answer/",       SubmitAnswerView.as_view(),   name="attempt-answer"),
    path("<uuid:session_id>/submit/",       SubmitAttemptView.as_view(),  name="attempt-submit"),
    path("<uuid:session_id>/result/",       AttemptResultView.as_view(),  name="attempt-result"),
    path("history/",                        AttemptHistoryView.as_view(), name="attempt-history"),
]

from .views import (
    StartAttemptView,
    SubmitAnswerView,
    SubmitAttemptView,
    AttemptResultView,
    AttemptHistoryView,
    ExplainAnswerView,
)

urlpatterns = [
    path("start/",                          StartAttemptView.as_view(),   name="attempt-start"),
    path("<uuid:session_id>/answer/",       SubmitAnswerView.as_view(),   name="attempt-answer"),
    path("<uuid:session_id>/submit/",       SubmitAttemptView.as_view(),  name="attempt-submit"),
    path("<uuid:session_id>/result/",       AttemptResultView.as_view(),  name="attempt-result"),
    path("<uuid:session_id>/explain/",      ExplainAnswerView.as_view(),  name="attempt-explain"),
    path("history/",                        AttemptHistoryView.as_view(), name="attempt-history"),
]
