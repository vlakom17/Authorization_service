from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import LoginHistory
from app.api.auth import get_current_user

logs_router = APIRouter()

@logs_router.get("/login-history")
def get_login_history(
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    user_role = current_user.get("role")

    if user_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return db.query(LoginHistory).filter(LoginHistory.user_id == user_id).all()
