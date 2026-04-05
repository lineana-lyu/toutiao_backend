from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from models.news import News
from models.users import User


class Favorite(Base):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), nullable=False, comment="创建时间")

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="unique_favorite"),
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_news_idx", "news_id"),
    )

    def __repr__(self):
        return f"<Favorite(id={self.id},user_id={self.user_id},news_id={self.news_id},created_at={self.created_at})>"
