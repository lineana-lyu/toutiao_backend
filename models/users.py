from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import DateTime, func, Integer, String, Index, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        Index('username_UNIQUE', "username"),
        Index('phone_UNIQUE', "phone")
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户id")
    # Optional: 允许为空
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像",
                                                  default="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg")
    gender: Mapped[Optional[str]] = mapped_column(Enum("male", "female", 'unknown'), comment="性别", default="unknown")
    bio: Mapped[Optional[str]] = mapped_column(String(500), comment="简介", default="这个人很懒，什么也没留下")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")
    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),onupdate=func.now(),comment="插入时间")


class UserToken(Base):
    __tablename__ = "user_token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户token id")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), comment="用户ID")
    token: Mapped[str] = mapped_column(String(255), comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    created_at: Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),comment="创建时间")

    def __repr__(self):
        return f"<UserToken(id={self.id},user_id={self.user_id},token={self.token})>"



