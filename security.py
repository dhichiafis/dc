from datetime import datetime, timedelta, timezone
from typing import Annotated
from models.model import *
from models.schema import *
from jose import jwt,JWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from pwdlib import PasswordHash
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_hash = PasswordHash.recommended()


#note that the auth scheme must be preceded by the user url path lest it begins to generate error
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    user=db.query(User).filter(User.username==username).first()
    return user 


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token:str=Depends(oauth2_scheme),
    db:Session=Depends(connect)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        #role=payload.get('role')
        if username is None:
        #if username is None or role is None:
            raise credentials_exception
        token_data=TokenData(username=username)
        #token_data = TokenData(username=username,role=role)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
   # if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def RoleChecker(allowed_role:list['str']):
    def check_user(user:User=Depends(get_current_active_user)):
        if user.role.name.lower() not in allowed_role:
            raise HTTPException(
                detail='user with specified role does not exist',
                status_code=400
            )
        return user 
    return check_user
