from django.core.cache import cache
from django.utils import timezone
from .models import QuizTemplate, Question, Option
from apps.core.exceptions import ServiceError
from apps.ai_service.client import GeminiClient


def get_or_generate_quiz(topic: str, question_count: int, difficulty: str, title: str, user) -> QuizTemplate:

    cache_key = f"quiz_template:{topic.lower()}:{difficulty}:{question_count}"
    cached_id = cache.get(cache_key)

    if cached_id:
        try:
            existing = QuizTemplate.objects.get(id=cached_id, status="ready", is_active=True)
            return existing
        except QuizTemplate.DoesNotExist:
            cache.delete(cache_key)

    quiz = QuizTemplate.objects.create(
        created_by     = user,
        title          = title or f"{topic.title()} Quiz ({difficulty})",
        topic          = topic,
        difficulty     = difficulty,
        question_count = question_count,
        status         = "pending",
    )

    quiz.status = "generating"
    quiz.save(update_fields=["status", "updated_at"])

    try:
        _generate_and_save_questions(quiz)
        cache.set(cache_key, str(quiz.id), timeout=60 * 60 * 24)
    except Exception as e:
        quiz.status = "failed"
        quiz.save(update_fields=["status", "updated_at"])
        raise ServiceError(f"Quiz generation failed: {str(e)}")

    return quiz


def _generate_and_save_questions(quiz: QuizTemplate) -> None:

    client    = GeminiClient()
    questions = client.generate_quiz_questions(
        topic              = quiz.topic,
        count              = quiz.question_count,
        difficulty         = quiz.difficulty,
        quiz_template_id   = quiz.id,
    )

    for order, q_data in enumerate(questions, start=1):
        question = Question.objects.create(
            quiz        = quiz,
            text        = q_data["text"],
            explanation = q_data.get("explanation", ""),
            order       = order,
        )
        for opt_data in q_data["options"]:
            Option.objects.create(
                question   = question,
                text       = opt_data["text"],
                is_correct = opt_data["is_correct"],
            )

    quiz.status         = "ready"
    quiz.question_count = len(questions)
    quiz.save(update_fields=["status", "question_count", "updated_at"])


def get_quiz_with_questions(quiz_id: str, user) -> QuizTemplate:

    try:
        quiz = QuizTemplate.objects.prefetch_related(
            "questions__options"
        ).get(id=quiz_id, is_active=True)
    except QuizTemplate.DoesNotExist:
        raise ServiceError("Quiz not found.", code="not_found")

    if quiz.status != "ready":
        raise ServiceError(
            f"Quiz is not ready yet. Current status: {quiz.status}",
            code="quiz_not_ready"
        )

    return quiz


def delete_quiz(quiz_id: str, user) -> None:

    try:
        quiz = QuizTemplate.objects.get(id=quiz_id, is_active=True)
    except QuizTemplate.DoesNotExist:
        raise ServiceError("Quiz not found.", code="not_found")

    if user.role not in ("teacher", "admin"):
        raise ServiceError("You do not have permission to delete this quiz.", code="forbidden")

    if user.role == "teacher" and quiz.created_by != user:
        raise ServiceError("You can only delete your own quizzes.", code="forbidden")

    quiz.soft_delete()