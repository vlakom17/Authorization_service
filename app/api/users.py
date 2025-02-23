import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.users import get_user_by_email, update_user_by_chat
from app.schemas.api_schemas import UserCreate
from app.services.auth_dependency import get_current_user, get_current_user_vk, get_current_user_yandex
from app.database.database import get_db
from app.messaging.rabbitmq import send_message

user_router = APIRouter()

@user_router.get("/me")
def get_profile(user=Depends(get_current_user)):
    return {"email": user["sub"]}

@user_router.get("/me_ya")
def get_profile(user=Depends(get_current_user_yandex)):
    return {"email": user["sub"]}

@user_router.get("/me_vk")
def get_profile(user=Depends(get_current_user_vk)):
    return {"email": user["sub"]}


QUEUE_NAME = "registration_notifications"

@user_router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(user.email, db)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    new_user = update_user_by_chat(user.chat_id, user.email, user.password, user.name, db)


    message = {
        "user_id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "event": "user_registered"
    }

    send_message(QUEUE_NAME, json.dumps(message))
    return {"id": new_user.id, "email": new_user.email}
