from fastapi import FastAPI
from src.app.router.auth import router as auth_router
from src.app.router.todos import router as todo_router
from src.app.router.users import router as user_router
from src.app import models
from src.app.database import engine
from fastapi.staticfiles import StaticFiles

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/healthy")
def get_status():
    return {"status":"Healthy"}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(todo_router)


