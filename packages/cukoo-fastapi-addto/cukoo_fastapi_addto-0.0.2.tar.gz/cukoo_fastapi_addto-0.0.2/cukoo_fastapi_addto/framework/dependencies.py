# -*- encoding: utf-8 -*-
'''
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

from loguru import logger
from typing import Generator
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

ALGORITHM = "HS256"
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/api/v1/login/access-token")

def get_current_user(request: Request, token: str = Depends(reusable_oauth2)):
    # init exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # token_key
    token_key = request.app.container.config.security.secret_key()
    try:
        payload = jwt.decode(token, token_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = request.app.container.user.user_repository().get(user_id)
    if user is None:
        raise credentials_exception
    return user