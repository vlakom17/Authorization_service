from sqlalchemy.orm import Session
from app.models.models import LoginHistory

def log_user_login(db: Session, user_id: int):
    login_entry = LoginHistory(user_id=user_id)
    db.add(login_entry)
    db.commit()
    db.refresh(login_entry) 
    return login_entry

def log_failed_login(db: Session, user_id: str):
    failed_entry = LoginHistory(user_id=user_id, type="failed")
    db.add(failed_entry)
    db.commit()
    db.refresh(failed_entry)
    return failed_entry

