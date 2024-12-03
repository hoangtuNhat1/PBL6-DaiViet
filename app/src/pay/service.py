from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from src.db.models import Payment, User
from src.auth.service import UserService
from src.errors import UserNotFound, PaymentNotFound
from .schemas import CreatePaymentSchema, PaymentResponseSchema
from src.auth.schemas import UserResponse
from payos import PayOS, PaymentData
import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.environ.get("PAYOS_CLIENT_ID")
api_key = os.environ.get("PAYOS_API_KEY")
checksum_key = os.environ.get("PAYOS_CHECKSUM_KEY")
payOS = PayOS(client_id=client_id, api_key=api_key, checksum_key=checksum_key)

user_service = UserService()


class PayService:
    """
    Service class to manage payment operations such as creating and retrieving purchase orders.
    """

    def create_purchase_order(
        self,
        user: UserResponse,
        order_data: CreatePaymentSchema,
        db: Session,
    ) -> Payment:
        """
        Create a new purchase order in the database.

        Args:
            db (Session): The database session.
            order_data (CreatePaymentSchema): The data for creating a purchase order.

        Returns:
            Payment: The created payment object.

        Raises:
            SQLAlchemyError: If there is a database error during the creation of the payment.
        """
        try:
            payment = Payment(
                user_id=user.uid,
                amount=int(order_data.amount),
                status=order_data.status,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
            paymentData = PaymentData(
                orderCode=payment.id,
                amount=order_data.amount,
                description="Thanh toan don hang",
                cancelUrl="http://localhost:8000",
                returnUrl="http://localhost:8000",
            )
            paymentLinkData = payOS.createPaymentLink(paymentData = paymentData)
            self.update_payment_details(db=db, payment=payment, checkout_url=paymentLinkData.checkoutUrl, qr_code=paymentLinkData.qrCode)
            return payment
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Database error while creating purchase order: {str(e)}")

    def get_purchase_orders_by_user(
        self, db: Session, user_email: str
    ) -> list[Payment]:
        """
        Retrieve all purchase orders associated with a given user.

        Args:
            db (Session): The database session.
            user_email (str): The email address of the user.

        Returns:
            list[Payment]: A list of payment objects associated with the user.

        Raises:
            UserNotFound: If the user cannot be found.
        """
        user = user_service.get_user_by_email(user_email, db)
        if not user:
            raise UserNotFound()

        return db.query(Payment).filter_by(user_id=user.id).all()

    def update_purchase_order_status(
        self, db: Session, order_id: int, new_status: str
    ) -> bool:
        """
        Update the status of a specific purchase order.

        Args:
            db (Session): The database session.
            order_id (int): The ID of the purchase order.
            new_status (str): The new status for the order.

        Returns:
            bool: True if the update was successful.

        Raises:
            PaymentNotFound: If the purchase order cannot be found.
            Exception: If there is a database error during the update.
        """
        try:
            payment = db.query(Payment).filter_by(id=order_id).first()
            if not payment:
                raise PaymentNotFound()

            payment.status = new_status
            payment.updated_at = datetime.now()
            db.commit()
            db.refresh(payment)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(
                f"Database error while updating status for order {order_id}: {str(e)}"
            )

    def update_payment_details(
        self, db: Session, payment: Payment, checkout_url: str, qr_code: str
    ) -> bool:
        """
        Update the checkout URL and QR code for a specific purchase order.

        Args:
            db (Session): The database session.
            order_id (int): The ID of the purchase order.
            checkout_url (str): The new checkout URL.
            qr_code (str): The new QR code data.

        Returns:
            bool: True if the update was successful.

        Raises:
            PaymentNotFound: If the purchase order cannot be found.
            Exception: If there is a database error during the update.
        """
        try:
            if not payment:
                raise PaymentNotFound()

            payment.checkout_url = checkout_url
            payment.qr_code = qr_code
            payment.updated_at = datetime.now()
            db.commit()
            db.refresh(payment)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(
                f"Database error while updating details for order {order_id}: {str(e)}"
            )

    def get_user_by_payment_id(self, db: Session, payment_id: int) -> User:
        """
        Retrieve the user associated with a specific payment ID.

        Args:
            db (Session): The database session.
            payment_id (int): The ID of the payment.

        Returns:
            User: The user associated with the payment.

        Raises:
            PaymentNotFound: If the payment cannot be found.
            UserNotFound: If the user associated with the payment cannot be found.
        """
        try:
            # Find the payment first
            payment = db.query(Payment).filter_by(id=payment_id).first()
            if not payment:
                raise PaymentNotFound()

            # Find the user associated with the payment
            user = db.query(User).filter_by(uid=payment.user_id).first()
            if not user:
                raise UserNotFound()

            return user
        except SQLAlchemyError as e:
            raise Exception(f"Database error while retrieving user for payment {payment_id}: {str(e)}")
