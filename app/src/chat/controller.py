from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.auth.dependencies import get_current_user
from .service import ChatService
from .schemas import ChatRequest, ChatResponse
from src.auth.schemas import UserResponse
from src.history_logs.service import HistoryLogService

chat_router = APIRouter()
chat_service = ChatService()
log_service = HistoryLogService()


@chat_router.post("/", response_model=ChatResponse)
def chat_with_character(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    """
    Chat with a specific character.

    Args:
        chat_request (ChatRequest): The input data containing user ID, character ID, and the question.
        db (Session): Database session dependency.

    Returns:
        ChatResponse: The response containing the AI's answer.
    """
    prompt, answer = chat_service.chat_character(
        user_uid=user.uid,
        character_id=chat_request.character_id,
        question=chat_request.question,
        db=db,
    )
    log = log_service.create_history_log(
        db=db,
        user_id=user.uid,
        character_id=chat_request.character_id,
        question=chat_request.question,
        prompt=prompt,
        answer=answer,
    )
    return ChatResponse(answer=answer, log_id=log.id)
