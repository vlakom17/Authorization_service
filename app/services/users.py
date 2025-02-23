from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_user_by_email(email: str, db: Session):
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    return result.scalars().first()

def create_user(email: str, password: str, name: str, db: Session):
    if not password:
        raise ValueError("Password cannot be empty")
    
    hashed_password = pwd_context.hash(password)
    
    new_user = User(email=email, hashed_password=hashed_password, name=name)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def update_user_by_chat(chat_id: int, new_email: str, new_password: str, new_name: str, db: Session):

    user = db.query(User).filter(User.chat_id == chat_id).first()

    hashed_password = pwd_context.hash(new_password)
    if user:
        user.email = new_email
        user.hashed_password = hashed_password
        user.name = new_name
        db.commit()
        db.refresh(user)
        return user
    
    return None
