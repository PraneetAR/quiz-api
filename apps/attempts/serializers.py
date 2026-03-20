from rest_framework import serializers
from .models import QuizSession, QuestionResponse


class StartAttemptSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()


class SubmitAnswerSerializer(serializers.Serializer):
    question_id        = serializers.UUIDField()
    selected_option_id = serializers.UUIDField()
    time_taken_seconds = serializers.IntegerField(min_value=0, default=0)


class QuestionResponseSerializer(serializers.ModelSerializer):
    question_text  = serializers.CharField(source="question.text",         read_only=True)
    selected_text  = serializers.CharField(source="selected_option.text",  read_only=True)
    correct_option = serializers.SerializerMethodField()

    class Meta:
        model  = QuestionResponse
        fields = (
            "id", "question_text", "selected_text",
            "correct_option", "is_correct",
            "time_taken_seconds", "explanation_viewed"
        )

    def get_correct_option(self, obj):
        correct = obj.question.options.filter(is_correct=True).first()
        return correct.text if correct else None


class QuizSessionSerializer(serializers.ModelSerializer):
    quiz_title       = serializers.CharField(source="quiz.title",  read_only=True)
    quiz_topic       = serializers.CharField(source="quiz.topic",  read_only=True)
    percentage_score = serializers.FloatField(read_only=True)

    class Meta:
        model  = QuizSession
        fields = (
            "id", "quiz_title", "quiz_topic",
            "status", "score", "percentage_score",
            "total_questions", "correct_count",
            "time_taken_seconds", "completed_at",
            "created_at"
        )


class AttemptResultSerializer(serializers.ModelSerializer):
    quiz_title       = serializers.CharField(source="quiz.title", read_only=True)
    quiz_topic       = serializers.CharField(source="quiz.topic", read_only=True)
    percentage_score = serializers.FloatField(read_only=True)
    responses        = QuestionResponseSerializer(many=True, read_only=True)

    class Meta:
        model  = QuizSession
        fields = (
            "id", "quiz_title", "quiz_topic",
            "status", "score", "percentage_score",
            "total_questions", "correct_count",
            "time_taken_seconds", "completed_at",
            "responses"
        )

class ExplainAnswerSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()        