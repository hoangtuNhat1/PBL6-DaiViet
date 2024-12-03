from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from .schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserRoleUpdate,
    UserBalanceIncrease,
)
from .service import UserService
from src.db.database import get_db
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.utils.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists, InvalidCredentials, InvalidToken
from .utils import verify_password, create_access_token

REFRESH_TOKEN_EXPIRY = 7
auth_router = APIRouter()
user_service = UserService()
all_role_checker = RoleChecker(["admin", "user"])
admin_role_checker = RoleChecker(["admin"])


@auth_router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreate, session: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user account.

    Args:
        user_data (UserCreate): The data for creating a new user.
        session (Session): The database session.

    Returns:
        UserResponse: The newly created user.
    """
    email = user_data.email
    if user_service.user_exists(email, session):
        raise UserAlreadyExists()
    new_user = user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_users(
    login_data: UserLogin, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Log in a user and generate access and refresh tokens.

    Args:
        login_data (UserLogin): The user's login credentials.
        db (Session): The database session.

    Returns:
        JSONResponse: A response containing tokens and user details.
    """
    email = login_data.email
    password = login_data.password
    user = user_service.get_user_by_email(email, db)
    if user and verify_password(password, user.password_hash):
        access_token = create_access_token(
            {"email": user.email, "user_uid": str(user.uid)}
        )
        refresh_token = create_access_token(
            {"email": user.email, "user_uid": str(user.uid)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        )
        return JSONResponse(
            content={
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"email": user.email, "uid": str(user.uid)},
            }
        )
    raise InvalidCredentials()


@auth_router.put("/update", response_model=UserUpdate)
async def update_user(
    user_update: UserUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserUpdate:
    """
    Update user details.

    Args:
        user_update (UserUpdate): The updated user data.
        user: The current logged-in user.
        db (Session): The database session.

    Returns:
        UserUpdate: The updated user data.
    """
    updated_user = user_service.update_user(user_update=user_update, user=user, db=db)
    return updated_user


@auth_router.put("/role", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_role(
    role_request: UserRoleUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_role_checker),
) -> UserResponse:
    """
    Update a user's role.

    Args:
        role_request (UserRoleUpdate): The role update request.
        db (Session): The database session.
        _: Admin role checker dependency.

    Returns:
        UserResponse: The updated user data.
    """
    user = user_service.update_role(
        email=role_request.email, new_role=role_request.role, db=db
    )
    return user


@auth_router.put(
    "/balance", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def increase_balance(
    balance_request: UserBalanceIncrease,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Increase a user's balance.

    Args:
        balance_request (UserBalanceIncrease): The balance increase request.
        db (Session): The database session.
        _: Admin role checker dependency.

    Returns:
        UserResponse: The updated user data.
    """
    user = user_service.increase_balance(
        email=balance_request.email, amount=balance_request.amount, db=db
    )
    return user

@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer()),
) -> JSONResponse:
    """
    Generate a new access token using a refresh token.

    Args:
        token_details (dict): Details of the refresh token.

    Returns:
        JSONResponse: A response containing the new access token.
    """
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise InvalidToken()


@auth_router.get("/logout")
async def revoke_token(
    token_details: dict = Depends(AccessTokenBearer()),
) -> JSONResponse:
    """
    Log out a user by revoking the token.

    Args:
        token_details (dict): Details of the access token.

    Returns:
        JSONResponse: A response indicating successful logout.
    """
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/buy-character/{character_id}", status_code=status.HTTP_200_OK)
async def buy_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    """
    Purchase a character.

    Args:
        character_id (int): The ID of the character to purchase.
        db (Session): The database session.
        current_user: The current logged-in user.

    Returns:
        dict: A response indicating the purchase status.
    """
    response, error = user_service.buy_character(
        user_uid=current_user.uid, character_id=character_id, db=db
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return response


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user(user=Depends(get_current_user)) -> UserResponse:
    """
    Retrieve details of the currently logged-in user.

    Args:
        user: The current logged-in user.

    Returns:
        UserResponse: The current user's details.
    """
    return user
