from fastapi import HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import add

from models.favorite import Favorite
from models.news import News
from schemas.favorite import FavoriteAddRequest


async def check_favorite(news_id: int, user_id:int,db: AsyncSession):
    query = select(Favorite).where(Favorite.news_id == news_id,Favorite.user_id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()
    return result is not None


async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    # 先检查是否已存在
    is_favorited = await check_favorite(news_id, user_id, db)
    if is_favorited:
        raise HTTPException(
            status_code=400,
            detail="已收藏该新闻，无需重复收藏"
        )
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def delete_news_favorite(news_id:int, user_id:int, db: AsyncSession):
    query = delete(Favorite).where(Favorite.news_id==news_id,Favorite.user_id==user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


async def get_user_favorites(
        user_id:int,
        page: int,
        page_size: int,
        db: AsyncSession):
    # 查总量->连表查询-->分页查询
    query = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    total = (await db.execute(query)).scalar_one()
    offset = (page - 1)*page_size
    # 连表查询select(查询表).join(关联表，关联条件).where().order_by()
    # Favorite.created_at.label("favorite_time"):取别名
    query = (select(News,Favorite.created_at.label("favorite_time"))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id)
             .order_by(Favorite.created_at.desc())
             .offset(offset)
             .limit(page_size))
    result = (await db.execute(query)).all()
    return result,total


# 清空用户收藏列表
async def clear_user_favorites(user_id: int, db: AsyncSession):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount



