from payos import PayOS, ItemData, PaymentData
import os
from dotenv import load_dotenv
load_dotenv()
client_id = os.environ.get('PAYOS_CLIENT_ID')
api_key = os.environ.get('PAYOS_API_KEY')
checksum_key = os.environ.get('PAYOS_CHECKSUM_KEY')
payOS = PayOS(client_id=client_id, api_key=api_key, checksum_key=checksum_key)
payOS.confirmWebhook("https://1c08-2402-800-629c-8662-5c42-1b4b-db9-6540.ngrok-free.app/api/v1/pay/webhook")
item = ItemData(name="Mì tôm hảo hảo ly", quantity=1, price=1000)

paymentData = PaymentData(orderCode=13, amount=1000, description="Thanh toan don hang",
     items=[item], cancelUrl="http://localhost:8000", returnUrl="http://localhost:8000")

paymentLinkData = payOS.createPaymentLink(paymentData = paymentData)
print(paymentLinkData)
print("Done")