from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Security, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError, encode, decode
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN
from db import session_scope, models

from api.user import User
from mappers.user import map_model_to_user

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
TOKEN_SUBJECT = "access"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    username: str = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    with session_scope() as s:
        s.expire_on_commit = False
        user = s.query(models.User).filter_by(username=username).first()
        return user


def authenticate_user(username: str, password: str) -> models.User:
    user = get_user(username)
    return user if user and verify_password(password, user.hashed_password) else False


def create_access_token(*, data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": TOKEN_SUBJECT})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Security(oauth2_scheme)) -> models.User:
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail="Could not validate credentials")
    user = get_user(username=token_data.username)
    return map_model_to_user(user) if user else None


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def route_login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
