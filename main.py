from fastapi import FastAPI, Request, Depends, Query
from fastapi.exceptions import HTTPException
from datetime import datetime
from pydantic import BaseModel
from db import SessionLocal
from sqlalchemy.orm import Session

from models import User, Post

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root(request: Request):
    return


@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    results = db.query(Post).join(User).all()
    return results


class PostDto(BaseModel):
    title: str
    content: str | None = None
    user_id: int


@app.post("/posts")
def addPost(post: PostDto, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    db.add(
        Post(
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            date_created=datetime.now(),
        )
    )
    db.commit()
    return post


class UserDto(BaseModel):
    name: str
    phone_number: str


@app.post("/users")
def addUser(user: UserDto, db: Session = Depends(get_db)):
    db.add(User(name=user.name, phone_number=user.phone_number))
    db.commit()
    return user


@app.get("/users")
def getUsers(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
