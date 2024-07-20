class TermosError(Exception):
    """Base class for all custom exceptions in the Unify application."""


class BadRequestError(TermosError):
    """Exception raised for HTTP 400 Bad Request errors."""


class AuthenticationError(TermosError):
    """Exception raised for HTTP 401 Unauthorized errors."""


class PermissionDeniedError(TermosError):
    """Exception raised for HTTP 403 Forbidden errors."""


class NotFoundError(TermosError):
    """Exception raised for HTTP 404 Not Found errors."""


class ConflictError(TermosError):
    """Exception raised for HTTP 409 Conflict errors."""


class UnprocessableEntityError(TermosError):
    """Exception raised for HTTP 422 Unprocessable Entity errors."""


class RateLimitError(TermosError):
    """Exception raised for HTTP 429 Too Many Requests errors."""


class InternalServerError(TermosError):
    """Exception raised for HTTP 500 Internal Server Error errors."""


status_error_map = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
    500: InternalServerError,
}
