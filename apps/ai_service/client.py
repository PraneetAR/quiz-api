import time
import json
from google import genai
from django.conf import settings

from .prompt_builder import build_quiz_prompt, build_explanation_prompt
from .validators import validate_ai_response
from apps.core.exceptions import AIServiceError
from .models import AIGenerationLog


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"
        self.max_retries = 3

    def generate_quiz_questions(
        self,
        topic: str,
        count: int,
        difficulty: str,
        quiz_template_id=None
    ) -> list:

        prompt = build_quiz_prompt(topic, count, difficulty)

        start_time = time.time()
        retry_count = 0
        last_error = ""

        while retry_count < self.max_retries:
            try:
                # ✅ UPDATED API CALL (no types config)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                raw_text = response.text
                parsed = self._parse_json_response(raw_text)

                # 🔥 IMPORTANT: handle {"questions": [...]}
                if isinstance(parsed, dict) and "questions" in parsed:
                    parsed = parsed["questions"]

                questions = validate_ai_response(parsed, count)

                latency_ms = int((time.time() - start_time) * 1000)

                self._log(
                    quiz_template_id=quiz_template_id,
                    prompt=prompt,
                    raw_response=raw_text,
                    status="success",
                    latency_ms=latency_ms,
                    retry_count=retry_count,
                )

                return questions

            except AIServiceError as e:
                last_error = e.message
                retry_count += 1
                time.sleep(1)

            except Exception as e:
                last_error = str(e)
                retry_count += 1
                time.sleep(2)

        latency_ms = int((time.time() - start_time) * 1000)

        self._log(
            quiz_template_id=quiz_template_id,
            prompt=prompt,
            raw_response="",
            status="failed",
            latency_ms=latency_ms,
            retry_count=retry_count,
            error_message=last_error,
        )

        raise AIServiceError(
            f"Quiz generation failed after {self.max_retries} attempts. Last error: {last_error}"
        )

    def generate_explanation(
        self,
        question_text: str,
        correct_answer: str,
        user_answer: str,
        topic: str
    ) -> dict:

        prompt = build_explanation_prompt(
            question_text, correct_answer, user_answer, topic
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            raw_text = response.text
            parsed = self._parse_json_response(raw_text)

            required_keys = ["explanation", "why_wrong", "concept", "follow_up_tip"]
            for key in required_keys:
                if key not in parsed:
                    parsed[key] = "Not available."

            return parsed

        except Exception:
            return {
                "explanation": "Unable to generate explanation at this time.",
                "why_wrong": "Please review the topic for more details.",
                "concept": topic,
                "follow_up_tip": "Try reviewing study materials on this topic.",
            }

    def _parse_json_response(self, raw_text: str) -> dict:

        text = raw_text.strip()

        # Remove markdown blocks if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]

        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise AIServiceError(f"AI returned invalid JSON. Parse error: {str(e)}")

    def _log(
        self,
        quiz_template_id,
        prompt: str,
        raw_response: str,
        status: str,
        latency_ms: int,
        retry_count: int,
        error_message: str = "",
        tokens_used: int = 0,
    ) -> None:

        try:
            AIGenerationLog.objects.create(
                quiz_template_id=quiz_template_id,
                prompt_used=prompt,
                raw_response=raw_response,
                status=status,
                latency_ms=latency_ms,
                retry_count=retry_count,
                error_message=error_message,
                tokens_used=tokens_used,
            )
        except Exception:
            pass