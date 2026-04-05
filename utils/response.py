from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse


def success_response(message: str = 'success', data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    # JSONResponse:是一个响应类，专门用于返回 JSON 格式的数据
    # jsonable_encoder:将任意 Python 对象转换为 JSON 兼容的数据类型
    return JSONResponse(content=jsonable_encoder(content))
