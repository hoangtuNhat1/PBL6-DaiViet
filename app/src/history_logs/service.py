from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from src.db.models import HistoryLog
from src.auth.service import UserService
from src.errors import UserNotFound, CharacterNotFound, LogNotFound
from src.db.models import Character
from .schemas import Feedback

user_service = UserService()


class HistoryLogService:
    """
    Service class to manage history log operations such as creating, retrieving, and updating history logs.
    """

    def create_history_log(
        self,
        db: Session,
        user_id: int,
        character_id: int,
        question: str,
        prompt: str,
        answer: str,
        feedback: str = None,
    ) -> HistoryLog:
        """
        Create a new history log entry in the database.

        Args:
            db (Session): The database session.
            user_id (int): The ID of the user creating the history log.
            character_id (int): The ID of the character associated with the history log.
            question (str): The question asked in the history log.
            prompt (str): The prompt provided in the history log.
            answer (str): The answer given in the history log.
            feedback (str, optional): The feedback (like/dislike) for the history log.

        Returns:
            HistoryLog: The created history log object.

        Raises:
            SQLAlchemyError: If there is a database error during the creation of the log.
        """
        try:
            history_log = HistoryLog(
                user_id=user_id,
                character_id=character_id,
                question=question,
                prompt=prompt,
                answer=answer,
                feedback=feedback,
                created_at=datetime.now(),
            )
            db.add(history_log)
            db.commit()
            return history_log
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def get_history_logs_by_user(self, db: Session, email: str) -> list[HistoryLog]:
        """
        Retrieve all history logs associated with a given user.

        Args:
            db (Session): The database session.
            email (str): The email address of the user to retrieve history logs for.

        Returns:
            list[HistoryLog]: A list of history log objects associated with the user.

        Raises:
            UserNotFound: If the user cannot be found.
        """
        user = user_service.get_user_by_email(email, db)
        if not user:
            raise UserNotFound()
        return db.query(HistoryLog).filter_by(user_id=user.uid).all()

    def get_history_logs_by_character(
        self, db: Session, character_id: int
    ) -> list[HistoryLog]:
        """
        Retrieve all history logs associated with a specific character.

        Args:
            db (Session): The database session.
            character_id (int): The ID of the character to retrieve history logs for.

        Returns:
            list[HistoryLog]: A list of history log objects associated with the character.

        Raises:
            CharacterNotFound: If the character cannot be found.
        """
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise CharacterNotFound()
        return db.query(HistoryLog).filter_by(character_id=character_id).all()

    def update_feedback(self, db: Session, log_id: int, feedback: Feedback) -> bool:
        """
        Update the feedback for a specific history log.

        Args:
            db (Session): The database session.
            log_id (int): The ID of the history log to update.
            feedback (Feedback): The feedback value ('like' or 'dislike').

        Returns:
            bool: True if the update was successful.

        Raises:
            LogNotFound: If the specified log ID does not exist.
            Exception: If there is a database error during the update.
        """
        try:
            history_log = db.query(HistoryLog).filter_by(id=log_id).first()
            if not history_log:
                raise LogNotFound()
            history_log.feedback = feedback
            db.commit()
            db.refresh(history_log)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(
                f"Database error while updating feedback for log {log_id}: {str(e)}"
            )
