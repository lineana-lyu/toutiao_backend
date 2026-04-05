from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewItemBase


class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., description="新闻ID", alias="newsId")


class HistoryAddResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    news_id: int = Field(alias="newsId")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class HistoryListResponse(BaseModel):
    list: list[NewItemBase]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
