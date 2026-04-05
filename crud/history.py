from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history_news(news_id: int, user_id: int, db: AsyncSession):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    existing_history = (await db.execute(query)).scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        # 拿着这个对象，去数据库查一遍它自己，把查到的最新数据覆盖回这个对象里
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


async def get_user_history(page: int, page_size: int, user_id: int, db: AsyncSession):
    # 计算浏览记录总量
    query = select(func.count(History.id)).where(History.user_id == user_id)
    total = (await db.execute(query)).scalar_one()
    # 计算分页里面需要跳过的记录数
    offset = (page - 1) * page_size
    # 查询当前页的浏览记录
    query = (select(News, History.view_time.label("viewTime"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset(offset)
             .limit(page_size))
    result = (await db.execute(query)).all()
    return result, total


async def del_one_history(
        news_id: int,
        user_id: int,
        db: AsyncSession
):
    query = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    await db.commit()

    return result.rowcount > 0


async def clear_user_history(user_id: int, db: AsyncSession):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount>0
