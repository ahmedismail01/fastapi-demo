from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas import UserDto, UserRead
from core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        UserRead(
            id=user.id,
            name=user.name,
            phone_number=user.phone_number,
            email=user.email,
        )
        for user in users
    ]
