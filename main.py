from telegram.ext import Application

from app.config import BOT_TOKEN, validate_config
from app.database import init_db
from app.handlers import setup_handlers


def build_application() -> Application:
    validate_config()
    app = Application.builder().token(BOT_TOKEN).build()
    setup_handlers(app)
    return app


def run_bot() -> None:
    init_db()
    app = build_application()
    print("Bot started successfully.")
    app.run_polling()
