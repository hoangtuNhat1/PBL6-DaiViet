import uuid
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    func,
    Float,
    Enum,
    Text,
    Table,
    ForeignKey,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Bảng liên kết giữa người dùng và nhân vật (Nhiều - Nhiều)
user_character_association = Table(
    "user_character",
    Base.metadata,
    Column("user_uid", String(36), ForeignKey("user_accounts.uid"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
)


class User(Base):
    """
    Bảng User lưu trữ thông tin cơ bản của người dùng và thiết lập các quan hệ với các bảng khác.
    """

    __tablename__ = "user_accounts"

    uid = Column(
        String(36),
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        info={"description": "Unique identifier for each user"},
    )
    username = Column(
        String(255), nullable=False, info={"description": "Username of the user"}
    )
    name = Column(String(255), nullable=True, info={"description": "Name of the user"})
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        info={"description": "User's email address"},
    )
    password_hash = Column(
        String(255),
        nullable=False,
        info={"description": "Hashed password for security"},
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        info={"description": "Account creation timestamp"},
    )

    # Vai trò và số dư tài khoản người dùng
    role = Column(
        String(50),
        nullable=False,
        default="user",
        info={"description": "Role of the user, e.g., 'admin', 'user', or 'guest'"},
    )
    balance = Column(
        Float, default=0.0, info={"description": "Balance in the user's account"}
    )

    characters = relationship(
        "Character",
        secondary=user_character_association,
        back_populates="users",
        info={"description": "List of characters associated with the user"},
    )

    history_logs = relationship(
        "HistoryLog",
        back_populates="user",
        info={"description": "User's activity logs"},
    )
    
    purchase_orders = relationship(
        "Payment",
        back_populates="user",
        info={"description": "List of purchase orders associated with the user"}
    )


class Character(Base):
    """
    Bảng Character lưu trữ thông tin về các nhân vật và thiết lập quan hệ với các bảng khác.
    """

    __tablename__ = "characters"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        info={"description": "Unique identifier for each character"},
    )
    short_name = Column(
        String(255), nullable=False, info={"description": "Short name of the character"}
    )
    name = Column(
        String(255), nullable=False, info={"description": "Full name of the character"}
    )
    description = Column(
        Text,
        nullable=True,
        info={"description": "Detailed description of the character"},
    )
    background_image = Column(
        Text,
        nullable=True,
        info={"description": "URL of the character's background image"},
    )
    profile_image = Column(
        Text,
        nullable=True,
        info={"description": "URL of the character's profile image"},
    )
    original_price = Column(
        Float, nullable=True, info={"description": "Original price of the character"}
    )
    new_price = Column(
        Float, nullable=True, info={"description": "Discounted price of the character"}
    )
    percentage_discount = Column(
        Float,
        nullable=True,
        info={"description": "Discount percentage on the character"},
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        info={"description": "Creation timestamp"},
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        info={"description": "Timestamp for the last update"},
    )

    users = relationship(
        "User",
        secondary=user_character_association,
        back_populates="characters",
        info={"description": "List of users associated with the character"},
    )

    history_logs = relationship(
        "HistoryLog",
        back_populates="character",
        info={"description": "Character's activity logs"},
    )


class HistoryLog(Base):
    """
    Bảng HistoryLog ghi lại các hoạt động của người dùng liên quan đến nhân vật, bao gồm các câu hỏi và phản hồi.
    """

    __tablename__ = "history_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        info={"description": "Unique identifier for each log"},
    )
    user_id = Column(
        String(36),
        ForeignKey("user_accounts.uid"),
        nullable=False,
        info={"description": "User ID"},
    )
    character_id = Column(
        Integer,
        ForeignKey("characters.id"),
        nullable=False,
        info={"description": "Character ID"},
    )
    question = Column(
        Text,
        nullable=False,
        info={"description": "User's question regarding the character"},
    )
    prompt = Column(
        Text,
        nullable=False,
        info={"description": "Prompt or context provided to the user"},
    )
    answer = Column(
        Text, nullable=False, info={"description": "Answer given to the user"}
    )
    feedback = Column(
        Enum("like", "dislike", name="feedback_enum"),
        nullable=True,
        info={"description": "Feedback on the answer"},
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        info={"description": "Timestamp of log creation"},
    )

    user = relationship(
        "User",
        back_populates="history_logs",
        info={"description": "User associated with the log"},
    )
    character = relationship(
        "Character",
        back_populates="history_logs",
        info={"description": "Character associated with the log"},
    )


class Payment(Base):
    """
    Bảng Payment quản lý các đơn mua của người dùng.
    """

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        info={"description": "Unique identifier for each purchase order"},
    )
    user_id = Column(
        String(36),
        ForeignKey("user_accounts.uid"),
        nullable=False,
        info={"description": "ID của người dùng liên kết với đơn mua"},
    )
    amount = Column(
        Integer,
        nullable=False,
        info={"description": "Amount of the payment"}
    )
    status = Column(
        Enum("PENDING", "PAID", "CANCELLED", name="order_status_enum"),
        nullable=False,
        default="PENDING",
        info={"description": "Tình trạng của đơn mua: pending, completed, cancelled"},
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        info={"description": "Thời gian tạo đơn mua"},
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        info={"description": "Thời gian cập nhật cuối cùng của đơn mua"},
    )
    checkout_url = Column(
        String(2083),
        nullable=True,
        info={"description": "URL để thực hiện thanh toán cho đơn mua"},
    )
    qr_code = Column(
        String(2083),
        nullable=True,
        info={"description": "Dữ liệu QR code liên kết với đơn mua"},
    )

    user = relationship(
        "User",
        back_populates="purchase_orders",
        info={"description": "Người dùng liên kết với đơn mua"},
    )
