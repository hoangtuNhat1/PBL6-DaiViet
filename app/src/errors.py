from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Callable


class AuthException(Exception):
    """Base class for all authentication-related exceptions."""

    pass


class InvalidToken(AuthException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(AuthException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(AuthException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(AuthException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(AuthException):
    """User has provided an email for a user who exists during sign up."""

    pass


class UserNotFound(AuthException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(AuthException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(AuthException):
    """User does not have the necessary permissions to perform an action."""

    pass


class CharacterNotFound(AuthException):
    """Character Not found"""

    pass


class LogNotFound(AuthException):
    """Character Not found"""

    pass


class InvalidFileType(AuthException):
    """Invalid file type"""

    pass


class InsufficientBalance(AuthException):
    """Insufficient balance"""

    pass


class UserAlreadyOwnsCharacter(AuthException):
    """Insufficient balance"""

    pass


class UserNotOwnsCharacter(AuthException):
    """Insufficient balance"""

    pass


class PaymentNotFound(AuthException):
    """Payment has provided an email for a Payment who exists during sign up."""

    pass


def create_exception_handler(
    status_code: int, initial_detail: dict
) -> Callable[[Request, Exception], JSONResponse]:
    """Creates a JSON response for exceptions with a specific status code and detail message."""

    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        CharacterNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Character not found",
                "error_code": "character_not_found",
            },
        ),
    )
    app.add_exception_handler(
        PaymentNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Payment not found",
                "error_code": "payment_not_found",
            },
        ),
    )
    app.add_exception_handler(
        LogNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Log not found",
                "error_code": "log_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidFileType,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid file type",
                "error_code": "invalid_file_type",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientBalance,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "You do not have enough money to buy this",
                "error_code": "insufficient_balance",
            },
        ),
    )
    app.add_exception_handler(
        UserAlreadyOwnsCharacter,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "You already own the character",
                "error_code": "user_already_owns_character",
            },
        ),
    )

    app.add_exception_handler(
        UserNotOwnsCharacter,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "You do not own the character. Please purchase it first.",
                "error_code": "user_not_owns_character",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
