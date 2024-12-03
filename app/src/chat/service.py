from src.db.models import User, Character
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.errors import UserNotFound, CharacterNotFound, UserNotOwnsCharacter


# from src.AI.service import AIService
# ai_service = AIService()
class ChatService:
    """
    Service class to handle chat interactions between a user and a character.
    """

    def chat_character(
        self, user_uid: str, character_id: int, question: str, db: Session
    ) -> tuple[str, str]:
        """
        Allows a user to chat with a character by providing a question. The method validates
        if the user exists and owns the specified character, then returns a prompt and answer.

        Args:
            user_uid (str): The unique identifier of the user.
            character_id (int): The ID of the character the user wants to interact with.
            question (str): The question to ask the character.
            db (Session): The database session.

        Returns:
            tuple[str, str]: A tuple containing the prompt and answer from the character.

        Raises:
            UserNotFound: If the user with the specified UID does not exist.
            CharacterNotFound: If the character with the specified ID does not exist.
            UserNotOwnsCharacter: If the user does not own the specified character.
            SQLAlchemyError: If there is a database error during the process.
        """
        try:
            # Query user and character from the database
            user = db.query(User).filter(User.uid == user_uid).first()
            character = db.query(Character).filter(Character.id == character_id).first()

            # Check if the user exists
            if not user:
                raise UserNotFound()

            # Check if the character exists
            if not character:
                raise CharacterNotFound()

            # Check if the user owns the character
            if character not in user.characters:
                raise UserNotOwnsCharacter()

            character_short_name = character.short_name
            character_name = character.name
            prompt = "Please answer"
            answer = "I don't know"
            # prompt, answer = ai_service.rag(question, character_short_name, character_name)
            return prompt, answer

        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Database error: {str(e)}")
