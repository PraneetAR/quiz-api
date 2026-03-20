from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema
from apps.core.throttles import QuizGenerationThrottle

from .models import QuizTemplate
from .serializers import (
    QuizTemplateSerializer,
    QuizGenerateSerializer,
    QuestionSerializer,
)
from .services import (
    get_or_generate_quiz,
    get_quiz_with_questions,
    delete_quiz,
)
from apps.core.exceptions import ServiceError
from apps.core.pagination import StandardPagination


class QuizGenerateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes   = [QuizGenerationThrottle]

    @extend_schema(summary="Generate a new quiz using AI")
    def post(self, request):
        serializer = QuizGenerateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = get_or_generate_quiz(
                topic          = serializer.validated_data["topic"],
                question_count = serializer.validated_data["question_count"],
                difficulty     = serializer.validated_data["difficulty"],
                title          = serializer.validated_data.get("title", ""),
                user           = request.user,
            )
            return Response({
                "status":  "success",
                "message": "Quiz generated successfully.",
                "data":    QuizTemplateSerializer(quiz).data
            }, status=status.HTTP_201_CREATED)

        except ServiceError as e:
            return Response({
                "status":  "error",
                "message": e.message
            }, status=status.HTTP_400_BAD_REQUEST)

class QuizListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List all available quizzes")
    def get(self, request):
        queryset = QuizTemplate.objects.filter(
            status    = "ready",
            is_active = True
        )

        topic      = request.query_params.get("topic")
        difficulty = request.query_params.get("difficulty")
        search     = request.query_params.get("search")

        if topic:
            queryset = queryset.filter(topic__icontains=topic)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if search:
            queryset = queryset.filter(title__icontains=search)

        paginator = StandardPagination()
        page      = paginator.paginate_queryset(queryset, request)

        serializer = QuizTemplateSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get quiz details with all questions")
    def get(self, request, quiz_id):
        try:
            quiz       = get_quiz_with_questions(quiz_id, request.user)
            questions  = quiz.questions.filter(is_active=True).order_by("order")
            return Response({
                "status": "success",
                "data": {
                    "quiz":      QuizTemplateSerializer(quiz).data,
                    "questions": QuestionSerializer(questions, many=True).data,
                }
            })
        except ServiceError as e:
            code = status.HTTP_404_NOT_FOUND if e.code == "not_found" else status.HTTP_400_BAD_REQUEST
            return Response({
                "status":  "error",
                "message": e.message
            }, status=code)

    @extend_schema(summary="Delete a quiz (teacher/admin only)")
    def delete(self, request, quiz_id):
        try:
            delete_quiz(quiz_id, request.user)
            return Response({
                "status":  "success",
                "message": "Quiz deleted successfully."
            })
        except ServiceError as e:
            code = status.HTTP_403_FORBIDDEN if e.code == "forbidden" else status.HTTP_404_NOT_FOUND
            return Response({
                "status":  "error",
                "message": e.message
            }, status=code)


class MyQuizzesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List quizzes created by current user")
    def get(self, request):
        queryset = QuizTemplate.objects.filter(
            created_by = request.user,
            is_active  = True
        ).order_by("-created_at")

        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(queryset, request)
        serializer = QuizTemplateSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)