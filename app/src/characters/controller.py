from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from .service import CharacterService
from src.auth.dependencies import RoleChecker, get_current_user
from .schemas import (
    CharacterCreate,
    CharacterResponse,
    CharacterUpdate,
    CharacterListResponse,
)
from src.auth.schemas import UserResponse
from typing import Dict
from src.errors import CharacterNotFound, InsufficientBalance, UserAlreadyOwnsCharacter

admin_role_checker = RoleChecker(["admin"])
user_role_checker = RoleChecker(["user"])
admin_or_user_role_checker = RoleChecker(["admin", "user"])
character_service = CharacterService()
char_router = APIRouter()


@char_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CharacterResponse,
)
async def create_character(
    character: CharacterCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_role_checker),
):
    db_character = character_service.create_character(character=character, db=db)
    return db_character


@char_router.put("/{character_id}/images", response_model=CharacterResponse)
async def update_images(
    character_id: int,
    pf_img: UploadFile = File(...),
    bg_img: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: bool = Depends(admin_role_checker),
):
    """
    Update the profile and background images for a character.
    """
    character = character_service.update_images(character_id, pf_img, bg_img, db)
    return character


@char_router.put("/{character_id}", response_model=CharacterResponse)
async def update_character_route(
    character_id: int,
    character_update: CharacterUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_role_checker),
):
    """
    Update a character's details.
    """
    updated_character = character_service.update_character(
        character_id, character_update, db
    )
    return updated_character


@char_router.get("/users", response_model=CharacterListResponse)
def get_user_characters(
    user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(admin_or_user_role_checker),
):
    """
    Get a list of characters associated with a specific user.
    """
    characters = character_service.get_user_characters(user, db)
    return {"characters": characters}


@char_router.post("/buy-character/{character_id}", response_model=Dict[str, str])
def buy_character(
    character_id: int,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
):
    """
    Endpoint for a user to buy a character.

    Args:
        character_id (int): The ID of the character to buy.
        db (Session): The database session.
        user (UserResponse): The user trying to buy the character.

    Returns:
        dict: A message indicating the success or failure of the purchase.
    """
    try:
        result = character_service.buy_character(user, character_id, db)
        return result
    except CharacterNotFound as e:
        raise e
    except UserAlreadyOwnsCharacter as e:
        raise e
    except InsufficientBalance as e:
        raise e
