from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLALCHEMY_BASE_URL = "sqlite:///./database.db"
# SQLALCHEMY_BASE_URL = 'postgresql://postgres:postgres_pass@localhost/fast_api_todo_project' # Postgresql uchun
# SQLALCHEMY_BASE_URL = 'mysql+pymysql://root:mysql_pass@127.0.0.1:3306/fast_api_todo_project' # Mysql uchun
SQLALCHEMY_BASE_URL = 'postgresql://ftfwefxr:Dq9iVBkGkJQa8xs1L3dzNicghwu7cLSe@batyr.db.elephantsql.com/ftfwefxr'


engine = create_engine(SQLALCHEMY_BASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
