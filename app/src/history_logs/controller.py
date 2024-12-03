from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.db.database import get_db
from src.auth.dependencies import RoleChecker
from .service import HistoryLogService
from .schemas import HistoryLogResponse, FeedbackRequest

# Initialize router and services
log_router = APIRouter()
history_service = HistoryLogService()
admin_role_checker = RoleChecker(["admin"])
user_role_checker = RoleChecker(["user"])
admin_or_user_role_checker = RoleChecker(["admin", "user"])
char_router = APIRouter()


@log_router.get("/user", response_model=List[HistoryLogResponse])
def get_user_history_logs(
    email: str, db: Session = Depends(get_db), _: bool = Depends(admin_role_checker)
):
    """
    Get history logs for a user by their email.

    Args:
        email (str): The user's email.
        db (Session): The database session dependency.

    Returns:
        List[HistoryLogResponse]: A list of history logs for the user.
    """
    history_logs = history_service.get_history_logs_by_user(db, email)
    return history_logs or []


@log_router.get("/character/{character_id}", response_model=List[HistoryLogResponse])
def get_character_history_logs(
    character_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_role_checker),
):
    """
    Get history logs for a specific character by its ID.

    Args:
        character_id (int): The character's ID.
        db (Session): The database session dependency.

    Returns:
        List[HistoryLogResponse]: A list of history logs for the character.
    """
    history_logs = history_service.get_history_logs_by_character(db, character_id)
    return history_logs or []


@log_router.put("/feedback/", response_model=bool)
def update_log_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_or_user_role_checker),
):
    """
    Update feedback for a specific history log.

    Args:
        log_id (int): The ID of the history log to update.
        feedback (Feedback): The feedback ('like' or 'dislike').
        db (Session): The database session dependency.

    Returns:
        bool: True if the update was successful.

    Raises:
        HTTPException: If the log is not found or if there is an internal error.
    """
    return history_service.update_feedback(db, request.id, request.feedback)
