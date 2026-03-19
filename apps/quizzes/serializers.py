from rest_framework import serializers
from .models import QuizTemplate, Question, Option
from apps.ai_service.validators import sanitize_topic


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Option
        fields = ("id", "text", "is_correct")


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model  = Question
        fields = ("id", "text", "explanation", "order", "options")


class QuizTemplateSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    question_count_actual = serializers.SerializerMethodField()

    class Meta:
        model  = QuizTemplate
        fields = (
            "id", "title", "topic", "difficulty",
            "question_count", "question_count_actual",
            "status", "total_attempts",
            "created_by", "created_at"
        )
        read_only_fields = (
            "id", "status", "total_attempts",
            "created_by", "created_at",
            "question_count_actual"
        )

    def get_question_count_actual(self, obj):
        return obj.questions.filter(is_active=True).count()


class QuizGenerateSerializer(serializers.Serializer):
    topic          = serializers.CharField(min_length=3, max_length=100)
    question_count = serializers.IntegerField(min_value=1, max_value=20)
    difficulty     = serializers.ChoiceField(
        choices=["easy", "medium", "hard"],
        default="medium"
    )
    title          = serializers.CharField(max_length=200, required=False)

    def validate_topic(self, value):
        try:
            return sanitize_topic(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))