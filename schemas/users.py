from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str=Field(max_length=72, description="密码最大长度为 72 个字符")



class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    model_config = ConfigDict(
        from_attributes=True  # 允许从ORM对象属性中取值
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoBase = Field(..., alias="userInfo")
    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias别名/字段名兼容
        from_attributes=True    # 允许从ORM对象属性中取值
    )


# 用户更新信息模型
class UserInfoUpdate(UserInfoBase):
    phone:Optional[str] = Field(None, max_length=20, description="手机号")



class UserUpatePassword(BaseModel):
    old_password: str=Field(...,description="旧密码",alias="oldPassword")
    new_password: str=Field(...,description="新密码",alias="newPassword")
    model_config = ConfigDict(populate_by_name=True)