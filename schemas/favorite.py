from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")
    model_config = ConfigDict(populate_by_name=True)


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")
    model_config = ConfigDict(populate_by_name=True)


class FavoriteAddResponse(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    news_id: int = Field(..., alias="newsId")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class FavoriteItemResponse(NewItemBase):
    favorite_time: datetime = Field(..., alias="favoriteTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


# 收藏列表响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteItemResponse]
    total: int
    has_moore: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
