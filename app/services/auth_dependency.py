from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


oauth2_scheme_yandex = OAuth2PasswordBearer(tokenUrl="/callback_yandex")

def get_current_user_yandex(token: str = Depends(oauth2_scheme_yandex)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


oauth2_scheme_vk = OAuth2PasswordBearer(tokenUrl="/callback_vk")

def get_current_user_vk(token: str = Depends(oauth2_scheme_vk)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload 

