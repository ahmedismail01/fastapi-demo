from datetime import date
from sqlalchemy import ForeignKey, String, Integer, Boolean ,DATE
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship , mapped_column
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer ,primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(50))
    email:Mapped[str] = mapped_column(String(50))
    password:Mapped[str] = mapped_column(String(100))
    posts: Mapped[List["Post"]] = relationship(
        "Post",back_populates="user", cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(Integer ,primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    content: Mapped[Optional[str]] = mapped_column(String(500))
    date_created: Mapped[date] = mapped_column(DATE)
    deleted: Mapped[bool] = mapped_column(Boolean , default = False)
    likes: Mapped[int] = mapped_column(Integer , default = 0)
    user_id: Mapped[int] =mapped_column(ForeignKey("user.id") ,nullable = False)
    user: Mapped["User"] = relationship("User" ,back_populates="posts")
