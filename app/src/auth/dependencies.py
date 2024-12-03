from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.utils.redis import token_in_blocklist
from src.db.database import get_db
from sqlalchemy.orm import Session
from .service import UserService
from typing import List, Any, Optional
from src.db.models import User
from src.errors import (
    InvalidToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    InsufficientPermission,
    UserNotFound,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    """
    A base class for token-based authentication using HTTP Bearer tokens.
    """

    def __init__(self, auto_error: bool = True) -> None:
        """
        Initialize the TokenBearer with auto-error behavior.

        Args:
            auto_error (bool): Whether to raise an error if authentication fails.
        """
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        """
        Validate the incoming request and decode the bearer token.

        Args:
            request (Request): The incoming request object.

        Returns:
            Optional[dict]: Decoded token data if valid.

        Raises:
            InvalidToken: If the token is invalid or in the blocklist.
        """
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)
        if not token_data:
            raise InvalidToken()
        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()
        if not self.token_valid(token):
            raise InvalidToken()

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        """
        Check if a token is valid.

        Args:
            token (str): The token to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data: dict) -> None:
        """
        Verify the decoded token data.

        Args:
            token_data (dict): Decoded token data.

        Raises:
            NotImplementedError: If not overridden in subclasses.
        """
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    """
    Class for validating access tokens.
    """

    def verify_token_data(self, token_data: dict) -> None:
        """
        Verify that the token is not a refresh token.

        Args:
            token_data (dict): Decoded token data.

        Raises:
            AccessTokenRequired: If the token is a refresh token.
        """
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    """
    Class for validating refresh tokens.
    """

    def verify_token_data(self, token_data: dict) -> None:
        """
        Verify that the token is a refresh token.

        Args:
            token_data (dict): Decoded token data.

        Raises:
            RefreshTokenRequired: If the token is not a refresh token.
        """
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the current user based on the access token.

    Args:
        token_details (dict): Decoded token data.
        db (Session): Database session.

    Returns:
        User: The current user object.

    Raises:
        UserNotFound: If the user is not found in the database.
    """

    user_email = token_details["user"]["email"]
    user = user_service.get_user_by_email(user_email, db)
    if not user:
        raise UserNotFound
    return user


class RoleChecker:
    """
    Dependency to check if the current user has the required role(s).
    """

    def __init__(self, allowed_roles: List[str]) -> None:
        """
        Initialize the RoleChecker with allowed roles.

        Args:
            allowed_roles (List[str]): List of allowed roles.
        """
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        """
        Check if the current user has one of the allowed roles.

        Args:
            current_user (User): The current authenticated user.

        Returns:
            bool: True if the user has the required role.

        Raises:
            InsufficientPermission: If the user does not have the required role.
        """
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
