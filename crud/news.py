from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cache_category, set_cache_categories, get_cache_news_list, set_cache_news_list
from models.news import Category, News
from schemas.base import NewItemBase


# 分类查询
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cache_category()
    if cached_categories:
        return cached_categories
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # 写入缓存
    if categories:
        # jsonable_encoder = 万能转换器，把任何复杂对象 → 变成 JSON 支持的格式
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    # 返回数据
    return categories


# 新闻每个分类列表查询
async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # 先尝试从缓存中获取新闻列表
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)
    if cached_list:
        # 该接口需要ORM对象
        return [News(**item) for item in cached_list]

    # 查询指定分类新闻的新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip * limit).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把ORM对象数据转换成字典才能写入缓存
        # ORM对象转成pydantic，再转成字典
        # by_alias=False:表示不适用别名，保存python风格，因为redis数据是给后端用的
        news_data = [NewItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list



# 新闻每个分类的总共数量查询
async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    total_count = result.scalar_one()  # 只能有一个结果，有零个或多个结果就会报错
    return total_count


# 获取特定新闻ID的新闻详情
async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 更新新闻的浏览量
async def update_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.flush()
    await db.commit()
    # rowcount 返回最近一次执行的 SQL 语句所影响的行数
    return result.rowcount > 0


# 获取指定新闻的相关新闻（即同类新闻）
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = (select(News).where(
        News.id != news_id,
        News.category_id == category_id).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit))
    result = await db.execute(stmt)
    detail_news = result.scalars().all()
    # return result.scalars().all()
    # 列表推导式：创建一个列表，列表的元素是执行一个表达式的结果
    # 将数据库查询到的 news 对象列表，转换为一个格式化的字典（dict）列表（筛选需要的字段）
    return [{
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "categoryId": news.category_id
    } for news in detail_news]