from .schemas import UserCreate, UserUpdate, UserResponse
from .utils import generate_password_hash
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.db.models import Character, User
from src.errors import UserNotFound
from typing import Optional


class UserService:
    def get_user_by_email(self, email: str, db: Session) -> User:
        """
        Retrieves a user by email from the database.

        Args:
            email (str): The email of the user.
            db (Session): The database session.

        Returns:
            User: The user object corresponding to the email, or None if not found.
        """
        return db.query(User).filter(User.email == email).first()

    def user_exists(self, email: str, db: Session) -> bool:
        """
        Checks if a user exists in the database by their email.

        Args:
            email (str): The email of the user.
            db (Session): The database session.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        user = self.get_user_by_email(email, db)
        return user is not None

    def create_user(self, user_data: UserCreate, db: Session) -> User:
        """
        Creates a new user and adds them to the database.

        Args:
            user_data (UserCreate): The data used to create the new user.
            db (Session): The database session.

        Returns:
            User: The newly created user object.
        """
        user_data_dict = user_data.model_dump()

        # Hash the password before saving it to the database
        user_data_dict["password_hash"] = generate_password_hash(
            user_data_dict.pop("password")
        )

        new_user = User(**user_data_dict)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    def update_user(
        self, user_update: UserUpdate, user: UserResponse, db: Session
    ) -> Optional[User]:
        """
        Updates an existing user's details in the database.

        Args:
            user_update (UserUpdate): The new data to update the user with.
            user (UserResponse): The existing user object to be updated.
            db (Session): The database session.

        Returns:
            Optional[User]: The updated user object, or None if the update fails.
        """
        user_data_dict = user_update.model_dump(exclude_unset=True)

        # Hash the password if it's included in the update
        if "password" in user_data_dict and user_data_dict["password"]:
            user_data_dict["password_hash"] = generate_password_hash(
                user_data_dict.pop("password")
            )

        # Apply the updates to the user
        for key, value in user_data_dict.items():
            setattr(user, key, value)

        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            return None

    def update_role(self, email: str, new_role: str, db: Session) -> Optional[User]:
        """
        Updates the role of a user.

        Args:
            email (str): The email of the user.
            new_role (str): The new role to assign to the user.
            db (Session): The database session.

        Returns:
            Optional[User]: The updated user object, or None if the update fails.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFound()

        user.role = new_role
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            return None

    def increase_balance(
        self, email: str, amount: float, db: Session
    ) -> Optional[User]:
        """
        Increases the balance of a user.

        Args:
            email (str): The email of the user.
            amount (float): The amount to add to the user's balance.
            db (Session): The database session.

        Returns:
            Optional[User]: The user object with the updated balance, or None if the user is not found.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None

        user.balance += amount
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            return None
