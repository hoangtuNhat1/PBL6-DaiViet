from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base as auth_base
from src.db.models import Base as char_base
from src.config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    auth_base.metadata.create_all(bind=engine)
    char_base.metadata.create_all(bind=engine)
    # association_base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
