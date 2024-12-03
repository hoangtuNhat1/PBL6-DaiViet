from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Schema representing the request to chat with a character.

    Attributes:
        character_id (int): The ID of the character to chat with.
        question (str): The question asked by the user.
    """

    character_id: int
    question: str


class ChatResponse(BaseModel):
    """
    Schema representing the response after chatting with a character.

    Attributes:
        prompt (str): The prompt returned by the character (e.g., their response).
        answer (str): The answer given by the character to the user's question.
        log_id (int): The ID of the log associated with this chat session.
    """

    answer: str
    log_id: int
