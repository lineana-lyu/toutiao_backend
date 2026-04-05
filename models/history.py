from datetime import datetime

from sqlalchemy import Integer, ForeignKey, func, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from models.users import User
from models.news import News

from models.base import Base


class History(Base):
    __tablename__ = "history"

    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id")
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="娴忚璁板綍ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, comment="鐢ㄦ埛ID")
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, comment="鏂伴椈ID")
    view_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), nullable=False, comment="娴忚鏃堕棿")

