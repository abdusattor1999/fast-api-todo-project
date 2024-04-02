from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, index=True, primary_key=True)
    title = Column(String(150))
    description = Column(String(600))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True)
    first_name = Column(String(25))
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String(120))
    phone = Column(String)
    role = Column(String(30))
