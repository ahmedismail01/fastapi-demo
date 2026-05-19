<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
from core.security import verify_password, create_access_token, hash_password
from db import get_db
from sqlalchemy.orm import Session
from schemas import RegisterDto,UserRead
from models import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(401, detail="Unauthorized")
    return {
        "access_token": create_access_token({"email": user.email, "id": user.id}),
        "success": True,
    }


@router.post("/register")
def register(register_dto: RegisterDto, db: Session = Depends(get_db)):
    existed_user = db.query(User).filter(User.email == register_dto.email).first()
    if existed_user:
        raise HTTPException(400, detail="user already exists")

    hashed_password = hash_password(register_dto.password)
    user = User(
        name=register_dto.name,
        phone_number=register_dto.phone_number,
        password=hashed_password,
        email=register_dto.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "data": UserRead(
        id=user.id,
        name=user.name,
        phone_number=user.phone_number,
        email=user.email,
    )}
=======
from fastapi import APIRouter, Depends, HTTPException
from core.security import verify_password, create_access_token, hash_password
from db import get_db
from sqlalchemy.orm import Session
from schemas import RegisterDto, UserRead
from models import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(401, detail="Unauthorized")
    return {
        "access_token": create_access_token({"email": user.email, "id": user.id}),
        "success": True,
    }


@router.post("/register")
def register(register_dto: RegisterDto, db: Session = Depends(get_db)):
    existed_user = db.query(User).filter(User.email == register_dto.email).first()
    if existed_user:
        raise HTTPException(400, detail="user already exists")

    hashed_password = hash_password(register_dto.password)
    user = User(
        name=register_dto.name,
        phone_number=register_dto.phone_number,
        password=hashed_password,
        email=register_dto.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "data": UserRead(
        id=user.id,
        name=user.name,
        phone_number=user.phone_number,
        email=user.email,
    )}
>>>>>>> 8b9766d (remove sensitive files)
