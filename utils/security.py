from passlib.context import CryptContext


# 创建密码上下文
# schemes：密码加密算法,deprecated="auto"：自动处理过时的算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 加密
def get_hash_password(password: str):
    return pwd_context.hash(password)


# 密码验证,返回的是布尔类型
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)








