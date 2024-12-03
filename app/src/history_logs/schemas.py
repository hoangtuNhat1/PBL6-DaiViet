from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Feedback(str, Enum):
    """
    Enum class to represent the feedback status provided by the user.

    Attributes:
        like (str): Represents a "like" feedback.
        dislike (str): Represents a "dislike" feedback.
    """

    like = "like"
    dislike = "dislike"


class HistoryLogResponse(BaseModel):
    """
    Pydantic model to represent the response structure for a history log entry.

    Attributes:
        id (int): The unique identifier of the history log.
        user_id (str): The identifier of the user associated with the log.
        character_id (int): The identifier of the character in the log.
        question (str): The question in the history log.
        prompt (str): The prompt provided in the history log.
        answer (str): The answer associated with the history log.
        feedback (Optional[Feedback]): The feedback on the history log, if provided.
        created_at (datetime): The timestamp of when the history log was created.
    """

    id: int
    user_id: str
    character_id: int
    question: str
    prompt: str
    answer: str
    feedback: Optional[Feedback]
    created_at: datetime

    class Config:
        orm_mode = True


class FeedbackRequest(BaseModel):
    """
    Pydantic model to represent the feedback submission request structure.

    Attributes:
        id (int): The unique identifier for the feedback request.
        feedback (Feedback): The feedback status provided by the user (like or dislike).
    """

    id: int
    feedback: Feedback

    class Config:
        orm_mode = True


class LogList(BaseModel):
    """
    Pydantic model to represent a list of history logs.

    Attributes:
        history_logs (List[HistoryLogResponse]): A list of history log responses.
    """

    history_logs: List[HistoryLogResponse]
