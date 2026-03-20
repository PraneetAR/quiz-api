from rest_framework.throttling import UserRateThrottle


class QuizGenerationThrottle(UserRateThrottle):
    scope = "quiz_generation"


class LoginThrottle(UserRateThrottle):
    scope = "login"