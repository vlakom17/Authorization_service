import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import User
from telegram import Update
from telegram.ext import Application, CommandHandler

load_dotenv()

async def start_command(update: Update, context, db: Session):

    chat_id = update.message.from_user.id
    existing_user = db.query(User).filter(User.chat_id == chat_id).first()
    if not existing_user:
        new_user = User(chat_id=chat_id, name=update.message.from_user.name)
        db.add(new_user)
        db.commit()
        await update.message.reply_text(f"Добро пожаловать в наш сервис! Ваш Telegram ID: {chat_id}, он понадобится вам при регистрации")

    else:
        await update.message.reply_text("Вы уже привязали свой Telegram аккаунт к нашему сервису!")

def main():

    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", lambda update, context: start_command(update, context, db=next(get_db()))))
    application.run_polling()

if __name__ == "__main__":
    main()

