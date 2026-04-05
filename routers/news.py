from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news

# 创建APIRouter实例
# prefix:路由前缀；tags:在http://127.0.0.1:8000/docs上的这个的分组
router = APIRouter(prefix="/api/news", tags=["news"])


# 接口实现流程
# 1. 在routers模块化路由 -> Api接口规范文档
# 2. 在conf配置创建数据库连接 -> 在models定义模型类->数据库表
# 3. 在crud封装操作数据库的方法
# 4. 在路由处理函数里面调用crud封装好的方法，响应结果

# 新闻分类目录
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    # 获取新闻分类列表
    categories = await news.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }


# 新闻不同分类的新闻列表
@router.get("/list")
async def list_get(
        # 函数的参数应该都是小写，alias为参数别名
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(default=10, le=100, alias="pageSize"),
        db: AsyncSession = Depends(get_db)):
    # offset跳过的新闻数量
    offset = (page - 1) * page_size
    # new_list:通过分类ID和跳过的数量找到当前页的新闻列表
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    # total_count:当前分类ID的新闻总数
    total_count = await news.get_news_count(db, category_id)
    # 判断这页后是否还有新闻
    if (offset + len(news_list)) >= total_count:
        has_more = False
    else:
        has_more = True
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total_count,
            "hasMore": has_more
        }
    }


# 新闻详情
@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., description="新闻ID", alias="id"),
        db: AsyncSession = Depends(get_db)):
    # 对浏览量加一，view_res用于判断是否增加浏览量成功
    view_res = await news.update_news_views(db, news_id)
    if not view_res:
        raise HTTPException(status_code=404,detail="添加浏览量失败")
    # news_detail：当前新闻ID的新闻详情内容
    news_detail = await news.get_news_detail(db, news_id)
    # 新闻ID不存在抛出异常
    if not news_detail:
        raise HTTPException(status_code=404,detail='该新闻不存在')
    # 根据新闻ID和该新闻的分类ID来找到相关新闻
    related_news = await news.get_related_news(db, news_id,news_detail.category_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news

        }
    }
