from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from core.config import dotenv_config

engine = create_engine(
    dotenv_config.get("database_url"),
    echo=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
