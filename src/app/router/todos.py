from fastapi import APIRouter, Depends, Path
import src.app.models as models
from src.app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from starlette import status
from .auth import get_current_user


class TodoRequest(BaseModel):
    title : str = Field(min_length=5)
    description : str = Field(min_length=5)
    priority : int = Field(le=5)
    complete : bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
router = APIRouter(prefix='/todo', tags=['ToDo'])


@router.get("")
async def read_all(user:user_dependency, db:db_dependency):
    return db.query(models.Todo).filter(models.Todo.owner_id==user.get('id')).all()

@router.get("/{id}")
async def retrieve_todo(db: db_dependency, id):
    todo_object = db.query(models.Todo).filter(models.Todo.id == id).first()
    if todo_object is not None:
        return todo_object
    else:
        raise HTTPException(status_code=404, detail="Todo not found!") 

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, db:db_dependency, data:TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ro'yxatdan o'tmagan foydalanuvchi")
    obj = models.Todo(**data.model_dump(), owner_id=user.get('id'))
    db.add(obj)
    db.commit()
    return {"success":True}

@router.put("/{id}")
async def update_todo(user:user_dependency, db:db_dependency, id:int, data:TodoRequest):
    if not user:
        raise HTTPException(status_code=401, detail="User is not authorized !")
    obj = db.query(models.Todo).filter(models.Todo.id == id).first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!")
    obj.title = data.title
    obj.description = data.description
    obj.priority = data.priority
    obj.complete = data.complete
    db.add(obj)
    db.commit()
    return {"success":True, "message":"Ish bitdi brat !"}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency, id:int=Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="User is not authorized !")
    obj = db.query(models.Todo).filter(models.Todo.id==id).filter(models.Todo.owner_id==user.get('id'))
    if obj.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!")
    obj.delete()
    db.commit()
    return {"success":True}

    