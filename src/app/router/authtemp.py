from fastapi import APIRouter, Depends, Form, Request, Response
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import src.app.models as models
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette import status
from starlette.responses import RedirectResponse
from .auth import authenticate, get_token_for_user, db_dependency, get_db, templates
import re

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
templates = Jinja2Templates(directory="src/templates")


SECRET_KEY = "5f4f873e4de6f072f2376d353582d5fbd008857cbc2e5ffcec849c54eed4f9fa"
ALGORITHM = "HS256"


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request : Request = request
        self.username : Optional[str] = None
        self.password : Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

async def get_current_user(request:Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return None
        return {"id":user_id, "username":username}
    except JWTError as e:
        pass
    

@router.post('/token')
async def login_for_access_token(response:Response, login_form:Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticate(login_form.username, password=login_form.password, db=db)
    if not user:
        return False
    token = get_token_for_user(user, expire=timedelta(days=3))
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True

@router.get("/login", response_class=HTMLResponse)
async def authpage(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("login.html", {"request": request})
    
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db:Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()

        response = RedirectResponse(url="/todotemp", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response=response, login_form=form, db=db)
        if not validate_user_cookie:
            msg = "User not fount with given credentials!"
            return templates.TemplateResponse("login.html", {"request":request, "msg":msg})
        return response
    except Exception as e: 
        msg = "Unknown Error"
        print(e)
        return templates.TemplateResponse("login.html", {"request":request, "msg":msg})

@router.get('/register', response_class=HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})

@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, phone:str=Form(...), 
                   username:str=Form(...), first_name:str=Form(...), password:str=Form(...),
                   password2:str=Form(...), db:Session = Depends(get_db)):
    validation1 = db.query(models.User).filter(models.User.username == username).first()
    validation2 = db.query(models.User).filter(models.User.phone == phone).first()
    if re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
        msg = "Phone number is incorrect !"
        return templates.TemplateResponse("register.html", {"request":request, "msg":msg})

    if validation1 or validation2:
        msg = "Username and Phone must be unique !!!"
        return templates.TemplateResponse("register.html", {"request":request, "msg":msg})
    if password != password2:
        msg = "Passwords must be same !!!"
        return templates.TemplateResponse("register.html", {"request":request, "msg":msg})
    hashed_password = bcrypt_context.hash(password)
    user = models.User(username=username, first_name=first_name, is_active=True, hashed_password=hashed_password, phone=phone,  role="user")
    db.add(user)
    db.commit()
    msg = "User created successfully !"
    return templates.TemplateResponse("login.html", {"request":request, "msg":msg})

@router.get('/logout', response_class=HTMLResponse)
def logout(request:Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request":request, "msg":msg})
    response.delete_cookie(key="access_token")
    return response

@router.get('/change-password', response_class=HTMLResponse)
def changepassword(request:Request):
    return templates.TemplateResponse("change_password.html", {"request":request})

@router.post('/change-password', response_class=HTMLResponse)
def changepassword(request:Request, username:str=Form(...), old_password:str=Form(...), new_password:str=Form(...), 
                   confirm_password:str=Form(...), db:Session = Depends(get_db)):
    if new_password != confirm_password:
        return templates.TemplateResponse("change_password.html", {"request":request, "msg":"Passwords must be same !!!"})
    user = authenticate(username, old_password, db)
    if not user:
        return templates.TemplateResponse("change_password.html", {"request":request, "msg":"Old password is incorrect !"})
    hashed_password = bcrypt_context.hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return templates.TemplateResponse("login.html", {"request":request, "msg":"Password changed successfully !"})