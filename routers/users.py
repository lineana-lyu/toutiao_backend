from fastapi import APIRouter, Query, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.users import update_user_info, update_password
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserInfoUpdate, UserUpatePassword
from crud import users
from utils.auth import get_current_user
from utils.response import success_response
from utils.security import verify_password

router = APIRouter(prefix='/api/user', tags=['user'])


@router.post("/register")
async def register(
        user_data: UserRequest = Body(..., description="用户信息"),
        db: AsyncSession = Depends(get_db)):
    # 注册逻辑：验证用户是否存在->不存在则创建用户->生成Token->返回用户信息
    existing_user = await users.check_user_exists(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.add_user(db, user_data)
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest = Body(..., description="用户信息"),
                db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user(user_info: UserInfoUpdate, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    update_user = await update_user_info(db, user.username, user_info)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(update_user))


@router.put("/password")
async def update_user_password(
        pwd_data: UserUpatePassword,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if not verify_password(pwd_data.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="旧密码错误")
    await update_password(db, user.username, pwd_data)
    return success_response(message="更新密码成功", data=None)
