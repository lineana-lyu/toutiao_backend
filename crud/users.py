import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, Update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User, UserToken
from schemas.users import UserRequest, UserInfoUpdate, UserUpatePassword
from utils.security import get_hash_password, verify_password


# 检索用户
async def check_user_exists(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 添加用户
async def add_user(db: AsyncSession, user_info: UserRequest):
    # 密码加密
    hashed_password = get_hash_password(user_info.password)
    user = User(username=user_info.username, password=hashed_password)
    db.add(user)
    await db.commit()
    # 刷新
    await db.refresh(user)
    return user


# 生成更新Token
async def create_token(db: AsyncSession, user_id: int):
    # uuid:专门用来生成绝对不会重复的随机字符串;返回的不是字符串，而是一个 UUID 对象
    # uuid4() 是最常用的生成方式，完全随机生成（安全级别最高）
    token = str(uuid.uuid4())
    # datetime.now():获取当前系统的本地时间；timedelta 是专门表示时间间隔的类
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()
    # 如果用户存在，更新令牌和有效时间
    if result:
        result.token = token
        result.expires_at = expires_at
    else:
        # 用户不存在，创建令牌用户
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token


# 验证用户存在且密码是否正确
async def authenticate_user(db: AsyncSession, user_data: UserRequest):
    user = await check_user_exists(db, user_data.username)
    if not user:
        return None
    # verify_password(输入未加密得密码，已经加密得密码)
    verify = verify_password(user_data.password, user.password)
    if not verify:
        return None
    return user


# 依据Token查询用户：验证Token->查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = (await db.execute(query)).scalar_one_or_none()
    # token不存在或已过期时直接返回None，避免对None访问属性导致500
    if (not result) or (result.expires_at < datetime.now()):
        return None
    query = select(User).where(User.id == result.user_id)
    result = (await db.execute(query)).scalar_one_or_none()
    return result


# 更新用户信息
async def update_user_info(db: AsyncSession, username: str, user_info: UserInfoUpdate):
    # user_info.model_dump():相当于user_info.__dict__
    # 没有设置值得不更新
    # exclude_unset=True：只包含客户端显式传递的字段，用于部分更新。
    # exclude_none=True：排除值为 None 的字段，可能导致清空操作被忽略。
    # 两者结合时，通常用于忽略 None 值的场景，但需根据业务需求判断。
    query = Update(User).where(User.username == username).values(
        **user_info.model_dump(exclude_unset=True, exclude_none=True))
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    user_update = await check_user_exists(db, username)
    return user_update


# 更新用户密码：验证旧密码是否正确->更新密码
async def update_password(db: AsyncSession, username: str, password: UserUpatePassword):
    password = get_hash_password(password.new_password)
    query = Update(User).where(User.username==username).values(password=password)
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    return await check_user_exists(db, username)

