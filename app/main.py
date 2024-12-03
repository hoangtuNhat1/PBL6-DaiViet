from fastapi import FastAPI, UploadFile
from src.utils.firebase import init_firebase
from src.db.database import init_db
from src.characters.controller import char_router
from src.auth.controller import auth_router
from src.chat.controller import chat_router
from src.history_logs.controller import log_router
from src.pay.controller import pay_router

from src.middleware import register_middleware
from src.errors import register_error_handlers

# Define API version
API_VERSION = "v1"


def lifespan(app: FastAPI):
    init_db()
    yield
    print("server is stopping")


app = FastAPI(lifespan=lifespan)
register_error_handlers(app)
register_middleware(app)
init_firebase()

app.include_router(
    char_router, prefix=f"/api/{API_VERSION}/characters", tags=["characters"]
)
app.include_router(auth_router, prefix=f"/api/{API_VERSION}/auth", tags=["auth"])
app.include_router(chat_router, prefix=f"/api/{API_VERSION}/chat", tags=["chat"])
app.include_router(log_router, prefix=f"/api/{API_VERSION}/log", tags=["log"])
app.include_router(pay_router, prefix=f"/api/{API_VERSION}/pay", tags=["pay"])