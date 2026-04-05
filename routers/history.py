from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.history import add_history_news, get_user_history, del_one_history, clear_user_history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryAddResponse, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
        new_data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    history = await add_history_news(new_data.news_id, user.id, db)
    return success_response(message="添加成功", data=HistoryAddResponse.model_validate(history))


@router.get("/list")
async def get_history_list(
        page: int = Query(default=1, gt=0, description="页码"),
        page_size: int = Query(default=10, le=100, gt=0, description="每页数量", alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    history, total = await get_user_history(page, page_size, user.id, db)
    history_list = [{
        **news.__dict__,
        "view_time": view_time
    } for news, view_time in history]
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取成功", data=data)


@router.delete("/delete/{history_id}")
async def delete_one_history(
        history_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    check__delete = await del_one_history(history_id,user.id,db)
    if not check__delete:
        raise HTTPException(status_code=400, detail="删除失败,该浏览记录不存在")
    return success_response(message="删除成功")


@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    result = await clear_user_history(user.id,db)
    if not result:
        raise HTTPException(status_code=400, detail="清空失败")
    return success_response(message="清空成功")

