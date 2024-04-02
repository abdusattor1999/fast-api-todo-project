from fastapi import APIRouter, Depends
from src.app.models import User
from src.app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from starlette import status
from .auth import get_current_user, authenticate, bcrypt_context
from pydantic import BaseModel, Field
import re

class ChangePasswordRequest(BaseModel):
    old_password : str
    new_password : str = Field(min_length=8)

class ChangePhoneRequest(BaseModel):
    phone : str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix='/user', tags=['User'])


@router.get("/get_user", status_code=200)
async def get_user_details(user:user_dependency, db:db_dependency):
    if not user:
        return {"success":False, "detail":"Not found"}
    return db.query(User).filter(User.id == user.get('id')).first()

@router.post("/change-password")
async def change_password(user:user_dependency, db:db_dependency, request:ChangePasswordRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    authed_user = authenticate(user.get("username"), request.old_password, db)
    if authed_user:
        authed_user.hashed_password = bcrypt_context.hash(request.new_password)
        db.add(authed_user)
        db.commit()
        return {"success":True, "detail":"Password has been changed"}
    raise HTTPException(status_code=400, detail="Password incorrect")

@router.put("/edit-phone/{phone}")
async def change_phone_number(user:user_dependency, db:db_dependency, phone:str):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = db.query(User).filter(User.username==user.get("username")).first()
    regexp_temp = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"
    if re.match(regexp_temp, phone):
        user.phone = phone
        db.add(user)
        db.commit()
        return {"success":True, "detail":f"Phone number updated to: {phone}"}
    raise HTTPException(status_code=400, detail="Phone number is incorrect !")