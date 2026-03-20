from django.utils import timezone
from django.db import transaction
from .models import QuizSession, QuestionResponse
from apps.quizzes.models import QuizTemplate, Question, Option
from apps.core.exceptions import ServiceError


def start_attempt(quiz_id: str, user) -> QuizSession:

    try:
        quiz = QuizTemplate.objects.get(id=quiz_id, status="ready", is_active=True)
    except QuizTemplate.DoesNotExist:
        raise ServiceError("Quiz not found or not ready.", code="not_found")

    existing = QuizSession.objects.filter(
        user   = user,
        quiz   = quiz,
        status = "in_progress"
    ).first()

    if existing:
        return existing

    session = QuizSession.objects.create(
        user            = user,
        quiz            = quiz,
        status          = "in_progress",
        total_questions = quiz.questions.filter(is_active=True).count(),
    )

    return session


def submit_answer(session_id: str, user, question_id: str, selected_option_id: str, time_taken: int) -> QuestionResponse:

    try:
        session = QuizSession.objects.get(id=session_id, user=user)
    except QuizSession.DoesNotExist:
        raise ServiceError("Session not found.", code="not_found")

    if session.status == "completed":
        raise ServiceError("This attempt is already completed.", code="already_completed")

    if session.status == "abandoned":
        raise ServiceError("This attempt has been abandoned.", code="abandoned")

    try:
        question = Question.objects.get(id=question_id, quiz=session.quiz, is_active=True)
    except Question.DoesNotExist:
        raise ServiceError("Question not found in this quiz.", code="not_found")

    try:
        selected_option = Option.objects.get(id=selected_option_id, question=question)
    except Option.DoesNotExist:
        raise ServiceError("Option not found for this question.", code="not_found")

    response, created = QuestionResponse.objects.update_or_create(
        session  = session,
        question = question,
        defaults = {
            "selected_option":    selected_option,
            "is_correct":         selected_option.is_correct,
            "time_taken_seconds": time_taken,
        }
    )

    return response


def submit_attempt(session_id: str, user) -> QuizSession:

    try:
        session = QuizSession.objects.prefetch_related(
            "responses__question__options"
        ).get(id=session_id, user=user)
    except QuizSession.DoesNotExist:
        raise ServiceError("Session not found.", code="not_found")

    if session.status == "completed":
        raise ServiceError("This attempt is already completed.", code="already_completed")

    with transaction.atomic():
        responses      = session.responses.all()
        correct_count  = sum(1 for r in responses if r.is_correct)
        total_time     = sum(r.time_taken_seconds for r in responses)

        session.correct_count       = correct_count
        session.total_questions     = session.quiz.questions.filter(is_active=True).count()
        session.score               = session.percentage_score
        session.time_taken_seconds  = total_time
        session.status              = "completed"
        session.completed_at        = timezone.now()
        session.save()

        session.quiz.total_attempts = session.quiz.sessions.filter(status="completed").count()
        session.quiz.save(update_fields=["total_attempts", "updated_at"])

        _update_analytics(session)

    return session


def get_attempt_result(session_id: str, user) -> QuizSession:

    try:
        return QuizSession.objects.prefetch_related(
            "responses__question__options",
            "responses__selected_option",
        ).get(id=session_id, user=user, status="completed")
    except QuizSession.DoesNotExist:
        raise ServiceError("Completed attempt not found.", code="not_found")


def get_attempt_history(user) -> list:

    return QuizSession.objects.filter(
        user=user
    ).select_related(
        "quiz",
        "user"
    ).prefetch_related(
        "responses__question",
        "responses__selected_option"
    ).order_by("-created_at")


def _update_analytics(session: QuizSession) -> None:

    from apps.analytics.models import TopicMastery
    from apps.users.models import UserPerformanceProfile

    topic = session.quiz.topic
    score = session.percentage_score

    mastery, _ = TopicMastery.objects.get_or_create(
        user  = session.user,
        topic = topic,
    )
    mastery.update_mastery(score)

    try:
        profile = session.user.performance
        profile.update_after_attempt(score)
    except UserPerformanceProfile.DoesNotExist:
        pass

def get_explanation(session_id: str, user, question_id: str) -> dict:

    from django.core.cache import cache
    from apps.ai_service.client import GeminiClient

    try:
        session = QuizSession.objects.get(
            id     = session_id,
            user   = user,
            status = "completed"
        )
    except QuizSession.DoesNotExist:
        raise ServiceError("Completed attempt not found.", code="not_found")

    try:
        response = QuestionResponse.objects.select_related(
            "question", "selected_option"
        ).get(session=session, question__id=question_id)
    except QuestionResponse.DoesNotExist:
        raise ServiceError("Question response not found.", code="not_found")

    if response.is_correct:
        raise ServiceError(
            "Explanations are only available for incorrect answers.",
            code="already_correct"
        )

    cache_key = f"explanation:{question_id}:{str(response.selected_option.id)}"
    cached    = cache.get(cache_key)

    if cached:
        return cached

    correct_option = response.question.options.filter(is_correct=True).first()

    client      = GeminiClient()
    explanation = client.generate_explanation(
        question_text  = response.question.text,
        correct_answer = correct_option.text if correct_option else "",
        user_answer    = response.selected_option.text,
        topic          = session.quiz.topic,
    )

    cache.set(cache_key, explanation, timeout=60 * 60 * 24 * 7)

    response.explanation_viewed = True
    response.save(update_fields=["explanation_viewed", "updated_at"])

    return explanation    