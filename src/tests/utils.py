from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from src.app.models import Base, Todo, User
from src.main import app
from src.app.router.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
import pytest
from src.app.router.auth import bcrypt_context

SQL_ALCHEMY_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQL_ALCHEMY_URL, 
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
    )

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"id":1, "username":"wwww", "role":"admin"}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todo(
        title="Test todo title",
        description="test description",
        priority=3,
        complete=False,
        owner_id=1
    )
    db = TestSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = User(
        username="test_user",
        first_name="Abdusattor",
        hashed_password=bcrypt_context.hash("password1313"),
        phone="+998993332211",
        role="admin"
    )
    db = TestSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

