from fastapi import FastAPI
from src.app.router.auth import router as auth_router
from src.app.router.authtemp import router as authtemp_router
from src.app.router.todos import router as todo_router
from src.app.router.users import router as user_router
from src.app.router.todos_temp import router as todo_temp_router
from src.app import models
from src.app.database import engine
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/healthy")
def get_status():
    return {"status":"Healthy"}

@app.get("/")
async def root():
    return RedirectResponse(url="/todotemp")

# app.include_router(auth_router)
app.include_router(authtemp_router)
app.include_router(user_router)
app.include_router(todo_router)
app.include_router(todo_temp_router)


