<<<<<<< HEAD
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from db import get_db
from fastapi.security import  OAuth2PasswordBearer
from core.security import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_access_token(token)

    email = payload.get("email")
    if not email:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

=======
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from db import get_db
from fastapi.security import  OAuth2PasswordBearer
from core.security import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_access_token(token)

    email = payload.get("email")
    if not email:
        raise HTTPException(401, "Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

>>>>>>> 8b9766d (remove sensitive files)
    return user