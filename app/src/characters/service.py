import os
from sqlalchemy.orm import Session
from src.db.models import Character, user_character_association
from .schemas import CharacterCreate, CharacterUpdate
from src.utils.firebase import upload_file_to_firebase
from src.errors import (
    CharacterNotFound,
    InvalidFileType,
    InsufficientBalance,
    UserAlreadyOwnsCharacter,
)
from fastapi import UploadFile
from src.auth.schemas import UserResponse
from sqlalchemy.exc import IntegrityError
from tempfile import NamedTemporaryFile


class CharacterService:

    def get_character(self, character_id: int, db: Session):
        return db.query(Character).filter(Character.id == character_id).first()

    def get_all_characters(self, db: Session):
        return db.query(Character)

    def create_character(self, character: CharacterCreate, db: Session):
        character = Character(
            short_name=character.short_name,
            name=character.name,
            description=character.description,
            original_price=character.original_price,
            new_price=character.new_price,
            percentage_discount=character.percentage_discount,
        )
        db.add(character)
        db.commit()
        db.refresh(character)
        return character

    def update_images(
        self, character_id: int, pf_img: UploadFile, bg_img: UploadFile, db: Session
    ) -> str:
        print(pf_img)
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise CharacterNotFound()
        if not pf_img.content_type.startswith("image/"):
            raise InvalidFileType
        if not bg_img.content_type.startswith("image/"):
            raise InvalidFileType
        temp_files = []
        profile_image_url = None
        background_image_url = None
        try:
            with NamedTemporaryFile(
                delete=False, suffix=f".{pf_img.filename.split('.')[-1]}"
            ) as tmp_pf_img:
                tmp_pf_img.write(pf_img.file.read())
                temp_files.append(tmp_pf_img.name)
                pf_img_path = tmp_pf_img.name
                if os.path.isfile(pf_img_path):
                    profile_image_url = upload_file_to_firebase(
                        pf_img_path,
                        f"profiles/{os.path.basename(pf_img_path)}",
                    )
                character.profile_image = profile_image_url
            with NamedTemporaryFile(
                delete=False, suffix=f".{bg_img.filename.split('.')[-1]}"
            ) as tmp_bg_img:
                tmp_bg_img.write(bg_img.file.read())
                temp_files.append(tmp_bg_img.name)
                bg_img_path = tmp_bg_img.name
                if os.path.isfile(bg_img_path):
                    background_image_url = upload_file_to_firebase(
                        bg_img_path,
                        f"profiles/{os.path.basename(bg_img_path)}",
                    )
                character.background_image = background_image_url
            db.commit()
        finally:
            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
        return character

    def update_character(
        self, character_id: int, character_update: CharacterUpdate, db: Session
    ):
        character = self.get_character(character_id, db)
        character_data_dict = character_update.model_dump(exclude_unset=True)
        if not character:
            return CharacterNotFound()
        for key, value in character_data_dict.items():
            setattr(character, key, value)
        db.commit()
        db.refresh(character)
        return character

    def delete_character(self, character_id: int, db: Session):
        character = self.get_character(character_id, db)
        if character:
            db.delete(character)
            db.commit()
        return character

    def get_user_characters(self, user: UserResponse, db: Session):
        """
        Fetch characters and determine ownership for the specified user.
        """
        # Query all characters and join with the user-character association table
        results = (
            db.query(Character, user_character_association.c.user_uid.label("user_uid"))
            .outerjoin(
                user_character_association,
                (user_character_association.c.character_id == Character.id)
                & (user_character_association.c.user_uid == user.uid),
            )
            .all()
        )

        # Process results into the desired structure
        characters = []
        for character, user_uid in results:
            characters.append(
                {
                    "id": character.id,
                    "short_name": character.short_name,
                    "name": character.name,
                    "description": character.description,
                    "background_image": character.background_image,
                    "profile_image": character.profile_image,
                    "original_price": character.original_price,
                    "new_price": character.new_price,
                    "percentage_discount": character.percentage_discount,
                    "own": user_uid is not None,  # True if the user owns this character
                }
            )
        return characters

    def buy_character(self, user: UserResponse, character_id: int, db: Session):
        """
        Allows a user to purchase a character if they have enough balance.

        Args:
            user_uid (str): The unique identifier of the user.
            character_id (int): The ID of the character to purchase.
            db (Session): The database session.

        Returns:
            tuple[Optional[dict], Optional[str]]: A tuple containing a success message or error message.
        """
        character = db.query(Character).filter(Character.id == character_id).first()

        if not character:
            raise CharacterNotFound()
        if character in user.characters:
            raise UserAlreadyOwnsCharacter()
        if user.balance < character.new_price:
            raise InsufficientBalance()

        user.balance -= character.new_price
        user.characters.append(character)

        try:
            db.commit()
            db.refresh(user)
            return {"msg": f"Character '{character.name}' purchased successfully."}
        except IntegrityError:
            db.rollback()
            return {"msg": "An error occurred while processing the transaction."}
