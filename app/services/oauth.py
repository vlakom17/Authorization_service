import requests
from sqlalchemy.orm import Session
from app.models.models import User
from fastapi import HTTPException, Depends
from app.services.history import log_failed_login
from app.database.database import get_db

def get_yandex_token(code, client_id, client_secret, redirect_uri, db: Session = Depends(get_db)):
    response = None
    url = "https://oauth.yandex.ru/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        log_failed_login(db, None)
        raise HTTPException(status_code=400, detail="Error exchanging code for access token")


def get_yandex_user_data(access_token):

    url = "https://login.yandex.ru/info"
    
    headers = {
        "Authorization": f"OAuth {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        if "id" not in user_data:
            raise ValueError("YAndex response does not contain an ID")
        return user_data
    else:
        if response.status_code != 200:
            raise Exception(f"Error fetching user data: {response.status_code}")



def create_user_from_yandex(user_data: dict, db: Session) -> User:

    email = None

    if 'default_email' in user_data:
        email = user_data['default_email']
    
    if not email and 'emails' in user_data and isinstance(user_data['emails'], list):
        email = user_data['emails'][0]

    if not email:
        email = f"user_{user_data.get('id', 'unknown')}_@yandex.com"
    
    db_user = db.query(User).filter(User.email == email).first()
    
    if not db_user:
        db_user = User(
            email=email,
            name=user_data.get('login', 'Anonymous'),
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        db_user.name = user_data.get('login', db_user.name)
        db_user.is_active = True
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user



def get_vk_user_data(user_id: int, access_token: str):
    user_info_url = "https://api.vk.com/method/users.get"
    params = {
        "user_ids": user_id,
        "access_token": access_token,
        "v": "5.131",
        "fields": "first_name,last_name"
    }
    response = requests.get(user_info_url, params=params)
    data = response.json()

    if "response" not in data:
        raise ValueError("Error fetching VK user data")

    user = data["response"][0]
    return {
        "id": user["id"],
        "name": f"{user['first_name']} {user['last_name']}"
    }

def create_user_from_vk(user_data: dict, db: Session) -> User:
    
    db_user = User(
        email=f"user_{user_data['name']}{user_data['id']}@vk.com",
        name=user_data["name"],
        is_active=True
    )
    db_user = db.query(User).filter(User.email == db_user.email).first()

    if db_user and db_user != None:
        return db_user
    else:
        db_user = User(
        email=f"user_{user_data['name']}{user_data['id']}@vk.com",
        name=user_data["name"],
        is_active=True
    )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user
