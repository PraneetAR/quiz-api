from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data

        if isinstance(errors, dict) and "detail" in errors:
            message = str(errors["detail"])
            code = getattr(errors.get("detail"), "code", "error")
            field_errors = {}
        else:
            message = "Validation failed. Please check the errors."
            code = "validation_error"
            field_errors = errors

        response.data = {
            "status":  "error",
            "code":    code,
            "message": message,
            "errors":  field_errors,
        }

    return response


class ServiceError(Exception):
    """
    Raised inside service layer when business logic fails.
    Views catch this and return a proper error response.
    """
    def __init__(self, message: str, code: str = "service_error"):
        self.message = message
        self.code    = code
        super().__init__(message)


class AIServiceError(Exception):
    """
    Raised when AI generation fails after all retries.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
