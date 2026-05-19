<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine(
    "sqlite:///app.db",
    echo=True,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
=======
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from core.config import dotenv_config

engine = create_engine(
    dotenv_config.get("database_url"),
    echo=True,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
>>>>>>> 8b9766d (remove sensitive files)
