from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import get_current_user
from db import get_db
from sqlalchemy.orm import Session

from models import User, Following

router = APIRouter(prefix="/following", tags=["following"])


def _user_payload(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "phone_number": user.phone_number,
        "email": user.email,
    }


def _following_payload(following: Following, related_user: User):
    return {
        "id": following.id,
        "user_id": following.user_id,
        "follower_id": following.follower_id,
        "user": _user_payload(related_user),
    }


@router.get("/")
def get_followings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    followings = (
        db.query(Following)
        .filter(Following.follower_id == current_user.id)
        .all()
    )
    return [
        _following_payload(following, following.user)
        for following in followings
    ]


@router.get("/followers")
def get_followers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    followers = (
        db.query(Following)
        .filter(Following.user_id == current_user.id)
        .all()
    )
    return [
        _following_payload(following, following.follower)
        for following in followers
    ]


@router.post("/follow/user/{user_id}")
def follow_user(user_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't follow yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_following = db.query(Following).filter(Following.follower_id == current_user.id,
                                              Following.user_id == user_id).first()
    if is_following:
        raise HTTPException(status_code=400, detail="User already following this user")

    following = Following(
        follower_id=current_user.id,
        user_id=user_id
    )
    db.add(following)
    db.commit()
    db.refresh(following)
    return _following_payload(following, user)


@router.post("/unfollow/user/{user_id}")
def unfollow_user(user_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't unfollow yourself")

    is_following = db.query(Following).filter(Following.follower_id == current_user.id,
                                              Following.user_id == user_id).first()
    if not is_following:
        raise HTTPException(status_code=400, detail="You don't follow this user")

    db.delete(is_following)
    db.commit()

    return {"message": "You have unfollowed this user"}
