from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import get_current_user
from db import get_db
from sqlalchemy.orm import Session

from models import User, Following

router = APIRouter(prefix="/following", tags=["following"])


@router.get("/")
def get_followings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    followings = db.query(Following).filter(Following.follower_id == current_user.id)
    return followings


@router.get("/followers")
def get_followers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    followings = db.query(Following).filter(Following.follower_id == current_user.id)
    return followings


@router.post("/follow/user/{user_id}")
def follow_user(user_id, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't follow yourself")

    is_following = db.query(Following).filter(Following.follower_id == current_user.id,
                                              Following.user_id == user_id).first()
    if is_following:
        raise HTTPException(status_code=400, detail="User already following this user")

    following = Following(
        following_id=current_user.id,
        user_id=user_id
    )
    db.add(following)
    db.commit()
    db.refresh(following)
    return following


@router.post("/unfollow/user/{user_id}")
def unfollow_user(user_id, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't unfollow yourself")

    is_following = db.query(Following).filter(Following.follower_id == current_user.id,
                                              Following.user_id == user_id).first()
    if not is_following:
        raise HTTPException(status_code=400, detail="You don't follow this user")

    db.delete(is_following)
    db.commit()

    return {"message": "You have unfollowed this user"}
