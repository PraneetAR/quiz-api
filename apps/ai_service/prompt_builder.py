def build_quiz_prompt(topic: str, count: int, difficulty: str) -> str:

    difficulty_guidance = {
        "easy":   "basic, straightforward questions suitable for beginners",
        "medium": "moderate questions requiring some understanding of the topic",
        "hard":   "challenging questions requiring deep knowledge and analysis",
    }

    guidance = difficulty_guidance.get(difficulty, difficulty_guidance["medium"])

    prompt = f"""
You are a quiz generation expert. Generate exactly {count} multiple choice questions about "{topic}".

Difficulty level: {difficulty} — {guidance}

STRICT RULES:
1. Return ONLY a valid JSON object. No explanations, no markdown, no code blocks.
2. Each question must have exactly 4 options.
3. Exactly ONE option must be correct per question.
4. The explanation must clearly state WHY the correct answer is right.
5. Questions must be unique and not repeat concepts.

Return this exact JSON structure:
{{
  "questions": [
    {{
      "text": "The full question text here?",
      "options": [
        {{"text": "First option",  "is_correct": false}},
        {{"text": "Second option", "is_correct": true}},
        {{"text": "Third option",  "is_correct": false}},
        {{"text": "Fourth option", "is_correct": false}}
      ],
      "explanation": "Clear explanation of why the correct answer is right."
    }}
  ]
}}

Topic: {topic}
Number of questions: {count}
Difficulty: {difficulty}
"""
    return prompt.strip()


def build_explanation_prompt(
    question_text: str,
    correct_answer: str,
    user_answer: str,
    topic: str
) -> str:

    prompt = f"""
A student answered a quiz question incorrectly. Help them understand their mistake.

Topic: {topic}
Question: {question_text}
Student's answer: {user_answer}
Correct answer: {correct_answer}

Provide a helpful explanation in this exact JSON format:
{{
  "explanation": "Clear explanation of why '{correct_answer}' is correct",
  "why_wrong": "Specific reason why '{user_answer}' is incorrect",
  "concept": "The core concept the student needs to understand",
  "follow_up_tip": "One practical tip to remember this for future"
}}

Return ONLY the JSON. No markdown, no extra text.
"""
    return prompt.strip()