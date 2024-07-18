# -*- encoding: utf-8 -*-
'''
@File    :   security.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, time, timedelta
from typing import Annotated

from fastapi import HTTPException, status
from pydantic import ValidationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def generate_token(data: dict, expires_delta: timedelta | None = None, secret_key: str | None = None) -> str:
    to_encode = data.copy()
    # valid time
    if not expires_delta:
        expires_delta = 15
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    # encode and update
    to_encode.update({"exp": expire})
    # jwt
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    # return
    return encoded_jwt

def parse_token(token: str, secret_key: str | None = None):
    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except (jwt.JWTError, ValidationError):
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"sub": 0}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)