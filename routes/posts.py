from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from db import get_db
from models import Following, Post, User
from schemas import PostDto, PostRead
from core.dependencies import get_current_user
from core.socket import manager

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostRead])
def get_posts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    results = (
        db.query(Post)
        .join(User)
        .filter(Post.user_id == current_user.id, Post.deleted.is_(False))
        .order_by(Post.date_created.desc(), Post.id.desc())
        .all()
    )
    return [
        PostRead(
            id=post.id,
            title=post.title,
            content=post.content,
            date_created=post.date_created,
            deleted=post.deleted,
            likes=post.likes,
            user_id=post.user_id,
        )
        for post in results
    ]


@router.get("/feed", response_model=list[PostRead])
def get_feed_posts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    followed_user_ids = [
        user_id
        for (user_id,) in db.query(Following.user_id)
        .filter(Following.follower_id == current_user.id)
        .all()
    ]
    results = (
        db.query(Post)
        .filter(
            Post.deleted.is_(False),
            or_(Post.user_id == current_user.id, Post.user_id.in_(followed_user_ids)),
        )
        .order_by(Post.date_created.desc(), Post.id.desc())
        .all()
    )
    return [
        PostRead(
            id=post.id,
            title=post.title,
            content=post.content,
            date_created=post.date_created,
            deleted=post.deleted,
            likes=post.likes,
            user_id=post.user_id,
        )
        for post in results
    ]


@router.post("/", response_model=PostRead)
async def add_post(post: PostDto, db: Session = Depends(get_db), current_user=Depends((get_current_user))):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    post_obj = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
        date_created=datetime.now().date(),
    )

    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    await manager.send_message_to_followers(
        type="post_created",
        data={
            "id": post_obj.id,
            "title": post_obj.title,
            "content": post_obj.content,
        },
        author=user.name,
        followers=user.followers,
    )
    return PostRead(
        id=post_obj.id,
        title=post_obj.title,
        content=post_obj.content,
        date_created=post_obj.date_created,
        deleted=post_obj.deleted,
        likes=post_obj.likes,
        user_id=post_obj.user_id,
    )
