from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import (
    StartAttemptSerializer,
    SubmitAnswerSerializer,
    QuizSessionSerializer,
    AttemptResultSerializer,
)
from .services import (
    start_attempt,
    submit_answer,
    submit_attempt,
    get_attempt_result,
    get_attempt_history,
)
from apps.core.exceptions import ServiceError
from apps.core.pagination import StandardPagination


class StartAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Start a quiz attempt")
    def post(self, request):
        serializer = StartAttemptSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = start_attempt(
                quiz_id = str(serializer.validated_data["quiz_id"]),
                user    = request.user,
            )
            return Response({
                "status":  "success",
                "message": "Attempt started.",
                "data":    QuizSessionSerializer(session).data
            }, status=status.HTTP_201_CREATED)

        except ServiceError as e:
            code = status.HTTP_404_NOT_FOUND if e.code == "not_found" else status.HTTP_400_BAD_REQUEST
            return Response({
                "status":  "error",
                "message": e.message
            }, status=code)


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Submit an answer for a question")
    def post(self, request, session_id):
        serializer = SubmitAnswerSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = submit_answer(
                session_id         = str(session_id),
                user               = request.user,
                question_id        = str(serializer.validated_data["question_id"]),
                selected_option_id = str(serializer.validated_data["selected_option_id"]),
                time_taken         = serializer.validated_data["time_taken_seconds"],
            )
            return Response({
                "status":     "success",
                "message":    "Answer submitted.",
                "is_correct": response.is_correct,
            })

        except ServiceError as e:
            code = status.HTTP_404_NOT_FOUND if e.code == "not_found" else status.HTTP_400_BAD_REQUEST
            return Response({
                "status":  "error",
                "message": e.message
            }, status=code)


class SubmitAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Finalize and submit a quiz attempt")
    def post(self, request, session_id):
        try:
            session = submit_attempt(
                session_id = str(session_id),
                user       = request.user,
            )
            return Response({
                "status":  "success",
                "message": "Attempt submitted successfully.",
                "data":    QuizSessionSerializer(session).data
            })

        except ServiceError as e:
            return Response({
                "status":  "error",
                "message": e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class AttemptResultView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get detailed results of a completed attempt")
    def get(self, request, session_id):
        try:
            session = get_attempt_result(
                session_id = str(session_id),
                user       = request.user,
            )
            return Response({
                "status": "success",
                "data":   AttemptResultSerializer(session).data
            })

        except ServiceError as e:
            return Response({
                "status":  "error",
                "message": e.message
            }, status=status.HTTP_404_NOT_FOUND)


class AttemptHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get current user attempt history")
    def get(self, request):
        sessions   = get_attempt_history(request.user)
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(sessions, request)
        serializer = QuizSessionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

from .services import (
    start_attempt,
    submit_answer,
    submit_attempt,
    get_attempt_result,
    get_attempt_history,
    get_explanation,
)
from .serializers import (
    StartAttemptSerializer,
    SubmitAnswerSerializer,
    QuizSessionSerializer,
    AttemptResultSerializer,
    ExplainAnswerSerializer,
)


class ExplainAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get AI explanation for a wrong answer")
    def post(self, request, session_id):
        serializer = ExplainAnswerSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            explanation = get_explanation(
                session_id  = str(session_id),
                user        = request.user,
                question_id = str(serializer.validated_data["question_id"]),
            )
            return Response({
                "status": "success",
                "data":   explanation
            })

        except ServiceError as e:
            code = status.HTTP_404_NOT_FOUND if e.code == "not_found" else status.HTTP_400_BAD_REQUEST
            return Response({
                "status":  "error",
                "message": e.message
            }, status=code)    