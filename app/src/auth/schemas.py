from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid
from datetime import datetime

# from src.characters.schemas import CharacterOutDB


class UserBase(BaseModel):
    """
    Base model providing the essential attributes for a user account,
    including identification and account details.
    """

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique identifier for the user account"
    )
    username: str = Field(..., max_length=255, description="Username of the user")
    name: Optional[str] = Field(None, max_length=255, description="Name of the user")
    email: EmailStr = Field(..., description="User's email address")
    password_hash: str = Field(
        ..., max_length=255, description="Hashed password of the user"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of account creation"
    )
    role: str = Field(
        default="user", description="Role of the user, e.g., 'admin', 'user'"
    )
    balance: Optional[float] = Field(
        default=0.0, description="Balance of the user account"
    )

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """
    Model for creating a new user account, with essential attributes such as
    first name, last name, username, email, and password.
    """

    name: str = Field(..., max_length=25, description="Name of the user")
    username: str = Field(..., description="Username of the user")
    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(
        ..., min_length=6, description="Password for the user account"
    )


class UserLogin(BaseModel):
    """
    Model containing the login information for the user, such as email and password.
    """

    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(
        ..., min_length=6, description="Password for the user account"
    )


# class UserCharacter(UserBase):
#     """
#     Model that extends UserBase and includes a list of characters associated with the user.
#     """

#     characters: List[CharacterOutDB] = Field(
#         ..., description="List of characters associated with the user"
#     )


class UserUpdate(BaseModel):
    """
    Model for updating user information, allowing modifications to name, username, and email.
    """

    name: Optional[str] = Field(None, max_length=255, description="Name of the user")
    username: Optional[str] = Field(
        None, max_length=255, description="Username of the user"
    )
    email: Optional[EmailStr] = Field(
        None, max_length=255, description="User's email address"
    )

    class Config:
        orm_mode = True


class UserRoleUpdate(BaseModel):
    """
    Model for updating the role of a user.
    """

    email: EmailStr = Field(..., description="User's email address")
    role: str = Field(..., description="Role of the user, e.g., 'admin', 'user'")

    class Config:
        orm_mode = True


class UserBalanceIncrease(BaseModel):
    """
    Model for increasing a user's account balance.
    """

    email: EmailStr = Field(..., description="User's email address")
    amount: float = Field(..., description="Amount to increase the user's balance")

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """
    Response model that includes the user's details after performing query actions.
    """

    uid: uuid.UUID = Field(..., description="Unique identifier for the user account")
    username: str = Field(..., description="Username of the user")
    email: EmailStr = Field(..., description="User's email address")
    name: Optional[str] = Field(None, description="Name of the user")
    role: str = Field(..., description="Role of the user, e.g., 'admin', 'user'")
    balance: float = Field(..., description="Balance of the user account")

    class Config:
        orm_mode = True
