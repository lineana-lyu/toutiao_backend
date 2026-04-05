from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.favorite import check_favorite, add_news_favorite, delete_news_favorite, get_user_favorites, \
    clear_user_favorites
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteAddResponse, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=['favorite'])


# 检查新闻收藏状态
@router.get("/check")
async def check_news_favorite(news_id: int = Query(..., description="新闻ID", alias="newsId"),
                              user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    is_favorited = await check_favorite(news_id, user.id, db)
    return success_response(message="检查新闻收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorited))


@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await add_news_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功", data=FavoriteAddResponse.model_validate(result))


@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., description="新闻ID", alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    is_delete = await delete_news_favorite(news_id, user.id, db)
    if not is_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏纪律不存在")
    return success_response(message="取消收藏成功")


# 获取新闻收藏列表（连表、分页）
@router.get("/list")
async def get_favorite_list(
        page: int = Query(default=1,gt=0),
        page_size: int = Query(default=10, gt=0,le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await get_user_favorites(user.id, page, page_size, db)
    has_more = total > page * page_size
    favorite_list = [{
        **news.__dict__,
        "favorite_time": favorite_time
    } for news, favorite_time in rows]
    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message="success", data=data)


@router.delete("/clear")
async def clear_favorite(
        user: User=Depends(get_current_user),
        db: AsyncSession=Depends(get_db)
):
    count = await clear_user_favorites(user.id,db)
    return success_response(message=f"成功删除{count}条收藏记录")
