import re
from apps.core.exceptions import AIServiceError


def validate_ai_response(data: dict, expected_count: int) -> list:

    if not isinstance(data, dict):
        raise AIServiceError("AI response is not a JSON object.")

    if "questions" not in data:
        raise AIServiceError("AI response missing 'questions' key.")

    questions = data["questions"]

    if not isinstance(questions, list):
        raise AIServiceError("'questions' must be a list.")

    if len(questions) == 0:
        raise AIServiceError("AI returned 0 questions.")

    validated = []

    for index, question in enumerate(questions):
        position = index + 1

        if not isinstance(question, dict):
            raise AIServiceError(f"Question {position} is not a valid object.")

        if not question.get("text", "").strip():
            raise AIServiceError(f"Question {position} has empty text.")

        options = question.get("options", [])

        if not isinstance(options, list) or len(options) != 4:
            raise AIServiceError(
                f"Question {position} must have exactly 4 options, got {len(options)}."
            )

        correct_options = [o for o in options if o.get("is_correct") is True]

        if len(correct_options) != 1:
            raise AIServiceError(
                f"Question {position} must have exactly 1 correct option, got {len(correct_options)}."
            )

        for opt_index, option in enumerate(options):
            if not option.get("text", "").strip():
                raise AIServiceError(
                    f"Question {position}, option {opt_index + 1} has empty text."
                )

        validated.append(question)

    return validated


def sanitize_topic(topic: str) -> str:

    sanitized = re.sub(r"[^\w\s\-.,]", "", topic)
    sanitized = re.sub(r"\s+", " ", sanitized)
    sanitized = sanitized.strip()

    if len(sanitized) < 3:
        raise ValueError("Topic must be at least 3 characters long.")

    if len(sanitized) > 100:
        sanitized = sanitized[:100]

    return sanitized