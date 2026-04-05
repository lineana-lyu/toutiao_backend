from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache

# 新闻相关的缓存方法：新闻分类的读取和写入
# key - value

CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY = "news:list:"


# 获取新闻分类缓存
async def get_cache_category():
    return await get_json_cache(CATEGORIES_KEY)


# 写入新闻分类缓存：缓存的数据，过期时间
# 分类、配置 7200；列表：600；详情：1800；验证码：120--数据越稳定，缓存越持久
async def set_cache_categories(data: List[Dict[str, Any]], expire=3600):
    return await set_cache(CATEGORIES_KEY, data, expire)


# 写入缓存-新闻列表 key = new_list:分类id：页码：每页数量 + 列表数据 + 过期时间
async def set_cache_news_list(category_id: int, page: int, page_size: int, new_list: List[Dict[str, Any]], expire=600):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY}{category_part}:{page}:{page_size}"
    return await set_cache(key, new_list, expire)


# 读取缓存-新闻列表
async def get_cache_news_list(category_id: Optional[int],page:int, page_size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)
