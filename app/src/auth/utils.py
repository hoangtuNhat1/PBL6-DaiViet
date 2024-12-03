from datetime import datetime, timedelta
import uuid
import logging
from passlib.context import CryptContext
import jwt
from src.config import Config
from itsdangerous import URLSafeTimedSerializer
from typing import Optional, Dict, Any

passwd_context = CryptContext(schemes=["bcrypt"])


def generate_password_hash(password: str) -> str:
    """
    Generates a hashed version of the provided password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    hash = passwd_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    """
    Verifies if the provided password matches the given hash.

    Args:
        password (str): The plain text password to verify.
        hash (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return passwd_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: Optional[timedelta] = None, refresh: bool = False
) -> str:
    """
    Creates an access token (JWT) containing user data, expiration time, and optional refresh flag.

    Args:
        user_data (dict): The user-specific data to embed in the token.
        expiry (Optional[timedelta]): The expiration time for the token. Defaults to 60 minutes.
        refresh (bool): Whether the token is a refresh token. Defaults to False.

    Returns:
        str: The generated JWT token as a string.
    """
    payload = {
        "user": user_data,
        "exp": datetime.now()
        + (expiry if expiry is not None else timedelta(minutes=60)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> Optional[dict]:
    """
    Decodes and validates the given JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Optional[dict]: The decoded token data if valid, or None if decoding fails.
    """
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)


def create_url_safe_token(data: dict) -> str:
    """
    Serializes a dictionary into a URL-safe token.

    Args:
        data (dict): The data to serialize into the URL-safe token.

    Returns:
        str: The serialized URL-safe token.
    """
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str) -> Optional[dict]:
    """
    Deserializes a URL-safe token into its original data.

    Args:
        token (str): The URL-safe token to decode.

    Returns:
        Optional[dict]: The decoded data if the token is valid, or None if decoding fails.
    """
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
        return None
