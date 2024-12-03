from pydantic import BaseModel, Field, UUID4, HttpUrl
from enum import Enum, unique
from typing import Optional
from datetime import datetime


class PayStatus(str, Enum):
    """Enumeration for the status of a purchase order."""

    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


@unique
class Amount(int, Enum):
    """Enumeration for purchase order amounts."""
    TEST = 3000
    TWO_HUNDRED = 200000
    FIVE_HUNDRED = 500000
    ONE_MILLION = 1000000
    TWO_MILLION = 2000000


class CreatePaymentSchema(BaseModel):
    """Schema for creating a new purchase order."""

    amount: Amount = Field(..., description="Amount of money for the purchase")
    status: PayStatus = Field(
        default=PayStatus.PENDING,
        description="Status of the purchase order",
    )

    class Config:
        orm_mode = True


class PaymentResponseSchema(BaseModel):
    """Schema for responding with purchase order data."""

    id: int = Field(..., description="Unique ID of the purchase order")
    user_id: UUID4 = Field(..., description="Unique ID of the user")
    amount: Amount = Field(..., description="Amount of money for the purchase")
    status: PayStatus = Field(..., description="Status of the purchase order")
    created_at: datetime = Field(..., description="Time the order was created")
    updated_at: datetime = Field(..., description="Last time the order was updated")
    checkout_url: Optional[HttpUrl] = Field(
        None,
        description="URL to process the payment for this purchase order",
    )
    qr_code: Optional[str] = Field(
        None,
        description="Data or link to the QR code associated with the purchase",
    )

    class Config:
        orm_mode = True
