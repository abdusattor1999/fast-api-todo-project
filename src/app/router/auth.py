from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from src.app.models import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.app.database import SessionLocal
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse



TIME_ZONE = "Asia/Tashkent"

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
templates = Jinja2Templates(directory="src/templates")


SECRET_KEY = "5f4f873e4de6f072f2376d353582d5fbd008857cbc2e5ffcec849c54eed4f9fa"
ALGORITHM = "HS256"

class Token(BaseModel):
    access_token: str
    token_type: str

def get_token_for_user(user, expire:timedelta):
    encode_data = {"sub":user.username, "id":user.id}
    encode_data.update({"exp":datetime.utcnow() + expire}) 
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Token is invalid")
        return {"id":user_id, "username":username}
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token is invalid")
    
user_dependency = Annotated[dict, Depends(get_current_user)]


def authenticate(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if user:
        if bcrypt_context.verify(password, user.hashed_password):
            return user


class UserRequest(BaseModel):
    username : str
    first_name : str
    is_active : bool
    phone : str
    password : str
    role : str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("")
async def register(db:db_dependency, request:UserRequest):
    user_exists = db.query(User).filter(User.username == request.username).first()
    if user_exists:
        return {"success":False, "error":"Username must be unique !!!"}
    
    user = User(
        username = request.username,
        first_name = request.first_name,
        is_active = request.is_active,
        phone = request.phone,
        hashed_password = bcrypt_context.hash(request.password),
        role = request.role
    )
    db.add(user)
    db.commit()
    return {'success':True}

@router.post('/token')
async def login_form(login_form:Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticate(login_form.username, password=login_form.password, db=db)
    if user:
        token = get_token_for_user(user, expire=timedelta(days=3))
        return {'access_token': token, 'token_type': 'bearer'}
    return {"success":False, "error":"User not fount with given credentials!"}





@router.get("/register", response_class=HTMLResponse)
async def authpage(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})