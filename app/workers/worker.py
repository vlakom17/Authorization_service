import os
from dotenv import load_dotenv
import functools
import json
import requests
from app.messaging.rabbitmq import get_connection
from app.database.database import get_db
from app.models.models import User
from sqlalchemy.orm import Session

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(user_id: int, message_text: str, db: Session):

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.chat_id:
        print(f"Ошибка: Не найден chat_id для user_id {user_id}")
        return

    chat_id = user.chat_id
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message_text}

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"Уведомление отправлено пользователю {user_id}")
    else:
        print(f"Ошибка отправки: {response.text}")

def callback(ch, method, properties, body, db: Session):
    try:
        data = json.loads(body)
        message = f"Вы успешно зарегестрированы под именем {data['name']}!"
        send_telegram_message(data['user_id'], message, db)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Ошибка обработки сообщения: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def setup_queue(channel, queue_name):
    
    channel.queue_declare(queue=queue_name, durable=True)

def consume_messages():

    connection, channel = get_connection()

    setup_queue(channel, 'registration_notifications')

    db = next(get_db())

    callback_with_db = functools.partial(callback, db=db)

    channel.basic_consume(queue='registration_notifications', on_message_callback=callback_with_db)

    print("Ожидание сообщений. Нажмите CTRL+C для выхода")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Прерывание работы...")
        connection.close()

if __name__ == "__main__":
    consume_messages()
