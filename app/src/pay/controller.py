from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .schemas import CreatePaymentSchema, PaymentResponseSchema, PayStatus
from .service import PayService, payOS
from src.auth.service import UserService
from src.db.database import get_db
from src.auth.dependencies import get_current_user
pay_router = APIRouter()
pay_service = PayService()
user_service = UserService()

@pay_router.post(
    "/create-payment",
    response_model=PaymentResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payment_data: CreatePaymentSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> PaymentResponseSchema:
    """
    Create a new payment for the logged-in user.

    Args:
        payment_data (CreatePaymentSchema): The payment data.
        db (Session): The database session.
        current_user: The logged-in user.

    Returns:
        PaymentResponseSchema: The created payment object.
    """
    payment = pay_service.create_purchase_order(
        user=current_user, order_data=payment_data, db=db
    )
    return payment

@pay_router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db),):
    try:
        webhook_body = await request.json()
        verified_data = payOS.verifyPaymentWebhookData(webhook_body)
        if verified_data.code == "00":
            pay_service.update_purchase_order_status(db=db, order_id=verified_data.orderCode, new_status=PayStatus.PAID)
            user = pay_service.get_user_by_payment_id(db=db, payment_id=verified_data.orderCode)
            user_service.increase_balance(email=user.email, amount=verified_data.amount,db=db)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))