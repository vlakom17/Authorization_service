from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.orm import relationship
from app.database.database import Base
from sqlalchemy import BigInteger


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=func.now())
    type = Column(String, default="successful")
    user = relationship("User", back_populates="login_history")


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    chat_id = Column(BigInteger, unique=True)
    role = Column(String, default="user")
    login_history = relationship("LoginHistory", back_populates="user")