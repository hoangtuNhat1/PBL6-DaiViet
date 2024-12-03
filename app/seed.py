from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.characters.service import CharacterService
from src.characters.schemas import CharacterCreate
from fastapi import UploadFile
import mimetypes
from tempfile import SpooledTemporaryFile
import os

character_service = CharacterService()


def create_upload_file(file_path: str) -> UploadFile:
    with open(file_path, "rb") as f:
        content = f.read()
    temp_file = SpooledTemporaryFile()
    temp_file.write(content)
    temp_file.seek(0)
    upload_file = UploadFile(file=temp_file, filename=os.path.basename(file_path))
    return upload_file


def seed_characters():
    db: Session = SessionLocal()
    character_image_dir = "images/character"
    if not os.path.exists(character_image_dir):
        print(f"Error: Directory {character_image_dir} does not exist!")
        return
    character_images = os.listdir(character_image_dir)
    for image_name in character_images:
        try:
            if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
                print(f"Skipping non-image file: {image_name}")
                continue
            short_name = os.path.splitext(image_name)[0]
            character = {
                "short_name": short_name,
                "name": short_name,
                "description": "Một vị tướng lý tưởng trong lịch sử Việt Nam là người hội tụ đủ tài năng quân sự, lòng yêu nước sâu sắc, và tinh thần hy sinh vì dân tộc. Ông là người dẫn dắt quân đội vượt qua những thử thách khắc nghiệt, chống lại kẻ thù mạnh hơn gấp bội, bảo vệ chủ quyền đất nước. Với trí tuệ xuất chúng, ông lập nên những chiến lược táo bạo, tận dụng địa hình, lòng dân và yếu tố bất ngờ để giành chiến thắng. Không chỉ là một nhà lãnh đạo tài ba, ông còn là một tấm gương đạo đức, truyền cảm hứng cho quân sĩ và nhân dân bằng lòng trung kiên và tinh thần đoàn kết. Sự nghiệp của ông trở thành biểu tượng của sự kiên cường và ý chí không khuất phục trước mọi khó khăn.",
                "original_price": 1000000,
                "new_price": 1000000,
                "percentage_discount": 0,
            }
            created_character = character_service.create_character(
                CharacterCreate(**character), db
            )
            image_path = os.path.join("images/character", image_name)
            profile_image = create_upload_file(image_path)
            background_image = create_upload_file(image_path)
            character_service.update_images(
                created_character.id, profile_image, background_image, db
            )
            print("Seed characters successfully!")
        except Exception as e:
            db.rollback()
            print(f"Error seeding characters: {e}")
        finally:
            db.close()


if __name__ == "__main__":
    seed_characters()
