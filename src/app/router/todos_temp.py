from fastapi import APIRouter, Depends, Form, Path, Request
from fastapi.responses import HTMLResponse
import src.app.models as models
from src.app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from starlette import status
from .auth import get_current_user
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette import status

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
templates = Jinja2Templates(directory="src/templates")
router = APIRouter(prefix='/todotemp', tags=['ToDo'])

@router.get('/test')
async def test_function(request:Request):
    return templates.TemplateResponse(request=request, name="edit-todo.html", context={'request':request})


@router.get("", response_class=HTMLResponse)
async def read_all(request:Request, db:Session = Depends(get_db)):
    todos = db.query(models.Todo).filter(models.Todo.owner_id==1).all()
    return templates.TemplateResponse("home.html", {"request":request, "todos":todos})

@router.get("/create", response_class=HTMLResponse)
async def create_todo(request:Request):
    return templates.TemplateResponse("add-todo.html", {"request":request})

@router.post("/create")
async def add_todo_post(request:Request, title:str=Form(...), description:str=Form(...), priority:int=Form(...), db:Session = Depends(get_db)):
    todo = models.Todo(title=title, description=description, priority=priority, complete=False, owner_id=1)
    db.add(todo)
    db.commit()
    return RedirectResponse(url="/todotemp", status_code=status.HTTP_302_FOUND)

@router.get("/edit/{id}", response_class=HTMLResponse)
async def edit_todo(request:Request, id:int, db:Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    return templates.TemplateResponse("edit-todo.html", {"request":request, 'todo':todo})

@router.post("/edit/{id}")
async def edit_todo_commit(request:Request, id:int, title:str=Form(...), description:str=Form(...), priority:int=Form(...), db:Session = Depends(get_db)):

    obj = db.query(models.Todo).filter(models.Todo.id == id).first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!")
    obj.title = title
    obj.description = description
    obj.priority = priority
    db.add(obj)
    db.commit()
    return RedirectResponse(url="/todotemp", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{id}", response_class=HTMLResponse, status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(request:Request, db:db_dependency, id:int=Path(gt=0)):
    obj = db.query(models.Todo).filter(models.Todo.id==id)
    obj.delete()
    db.commit()
    
    return RedirectResponse(url="/todotemp")

@router.get("/complete/{id}", response_class=HTMLResponse)
async def delete_todo(request:Request, db:db_dependency, id:int=Path(gt=0)):
    obj = db.query(models.Todo).filter(models.Todo.id==id).first()
    obj.complete = not obj.complete
    db.add(obj)
    db.commit()
    
    return RedirectResponse(url="/todotemp")