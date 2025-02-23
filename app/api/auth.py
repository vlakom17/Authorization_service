import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.schemas.api_schemas import LoginRequest
from datetime import timedelta
from app.database.database import get_db
from app.services.jwt import create_access_token, verify_password
from app.services.users import get_user_by_email
from app.services.auth_dependency import get_current_user
from app.services.history import log_user_login, log_failed_login
from app.services.oauth import create_user_from_yandex, get_yandex_user_data, get_vk_user_data, create_user_from_vk, get_yandex_token

load_dotenv()

auth_router = APIRouter()

@auth_router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):

    db_user = get_user_by_email(user.email, db)
    
    if not db_user:
        log_failed_login(db, None)
        raise HTTPException(status_code=401, detail="User not found")
    
    if not verify_password(user.password, db_user.hashed_password):
        log_failed_login(db, db_user.id)
        raise HTTPException(status_code=401, detail="Invalid password")

    
    log_user_login(db, db_user.id)

    admin_secret = os.getenv("ADMIN_SECRET_KEY")
    if user.secret_key and user.secret_key == admin_secret:
        db_user.role = "admin"

    db_user.is_active = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = create_access_token({"sub": db_user.email, "role": db_user.role}, expires_delta=timedelta(minutes=30))

    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}


@auth_router.post("/logout")
def logout(user=Depends(get_current_user), db: Session = Depends(get_db)):

    db_user = get_user_by_email(user["sub"], db)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    db_user.is_active = False
    db.add(db_user) 
    db.commit()
    
    return {"message": "User logged out successfully"}


@auth_router.get("/login_yandex")
def login_yandex():
    
    yandex_auth_url = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={os.getenv('YANDEX_CLIENT_ID')}&redirect_uri={os.getenv('YANDEX_REDIRECT_URI')}&scope=login:email"
    
    return {"auth_url": yandex_auth_url}


@auth_router.get("/callback_yandex")
def yandex_callback(code: str, db: Session = Depends(get_db)):
    try:

        token_data = get_yandex_token(code, client_id=os.getenv('YANDEX_CLIENT_ID'), 
                                      client_secret=os.getenv('YANDEX_CLIENT_SECRET'), 
                                      redirect_uri=os.getenv('YANDEX_REDIRECT_URI'), db=db)
        
        access_token = token_data['access_token']
        user_data = get_yandex_user_data(access_token)

        user = create_user_from_yandex(user_data, db)

        jwt_token = create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=30))

        log_user_login(db, user.id)

        return {"user_info": user_data, "access_token": jwt_token, "token_type": "bearer", "message": "User successfully logged in via Yandex"}
      
    except requests.exceptions.RequestException:
        if user.id:
            log_failed_login(db, user.id)
        else: log_failed_login(db, None)
        raise HTTPException(status_code=400, detail="Error exchanging code for access token")


@auth_router.get("/login_vk")
def login_vk():
    
    vk_auth_url = (
        "https://oauth.vk.com/authorize"
        f"?client_id={os.getenv('VK_CLIENT_ID')}"
        "&display=page"
        f"&redirect_uri={os.getenv('VK_REDIRECT_URI')}"
        "&response_type=code"
        "&v=5.131"
    )
    return RedirectResponse(vk_auth_url)


@auth_router.get("/callback_vk")
def vk_callback(code: str, db: Session = Depends(get_db)):
    try:
        token_url = "https://oauth.vk.com/access_token"
        params = {
            "client_id": os.getenv('VK_CLIENT_ID'),
            "client_secret": os.getenv('VK_CLIENT_SECRET'),
            "redirect_uri": os.getenv('VK_REDIRECT_URI'),
            "code": code
        }
        response = requests.get(token_url, params=params)
        token_data = response.json()

        if "access_token" not in token_data:
            log_failed_login(db, None)
            raise HTTPException(status_code=400, detail="Error VK authorization")

        access_token = token_data["access_token"]
        user_id = token_data["user_id"]

        user_data = get_vk_user_data(user_id, access_token)

        user = create_user_from_vk(user_data, db)
        jwt_token = create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=30))

        log_user_login(db, user.id)

        return {"user_info": user_data, "access_token": jwt_token, "token_type": "bearer", "message": "User successfully logged in via VK"}

    except requests.exceptions.RequestException:
        if user.id:
            log_failed_login(db, user.id)
        else: log_failed_login(db, None)
        raise HTTPException(status_code=400, detail="Error exchanging code for access token")


    
    