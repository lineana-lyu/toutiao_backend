# 头条新闻后端服务（FastAPI）

一个基于 **FastAPI + SQLAlchemy(Async) + MySQL + Redis** 的新闻业务后端示例项目，包含新闻浏览、用户认证、收藏与浏览历史等核心能力，适合学习异步 Python Web 开发与接口分层设计。

## 项目特性

- 异步 API：基于 FastAPI 与 SQLAlchemy AsyncSession
- 用户体系：注册、登录、Token 鉴权、个人信息与密码更新
- 新闻能力：新闻分类、分页列表、详情、相关资讯、浏览量更新
- 用户行为：收藏管理（查/增/删/清空）、浏览历史（查/增/删/清空）
- 缓存支持：Redis 缓存新闻分类和新闻列表
- 统一响应：统一 `code/message/data` 返回结构
- 全局异常：统一注册 HTTP、数据库与兜底异常处理

## 技术栈

- Python 3.10+（项目中本地环境为 3.13）
- FastAPI
- Uvicorn
- SQLAlchemy 2.x（Async）
- aiomysql
- Redis（`redis.asyncio`）
- Pydantic v2
- Passlib（bcrypt）

## 目录结构

```text
.
├── main.py                  # 应用入口
├── config/
│   ├── db_conf.py           # MySQL 异步连接与会话管理
│   └── cache_conf.py        # Redis 连接与缓存读写
├── models/                  # SQLAlchemy ORM 模型
├── schemas/                 # Pydantic 请求/响应模型
├── crud/                    # 数据访问层
├── routers/                 # 路由层
├── cache/                   # 业务缓存封装
├── utils/                   # 鉴权、响应、异常处理等工具
└── test_main.http           # 简单接口调试文件
```

## 快速开始

### 1. 克隆并进入项目

```bash
git clone <your-repo-url>
cd toutiao_backend
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

> 如需临时手动安装核心依赖：`pip install fastapi uvicorn sqlalchemy aiomysql redis pydantic passlib[bcrypt]`

### 3. 准备 MySQL 与 Redis

请确保本地服务已启动：

- MySQL：`localhost:3306`
- Redis：`localhost:6379`

当前代码默认配置（可在下列文件直接修改）：

- MySQL 连接串：`config/db_conf.py`
  - `mysql+aiomysql://your_username:your_password@localhost:3306/news_app?charset=utf8`
- Redis 配置：`config/cache_conf.py`
  - `host=localhost, port=6379, db=0`

### 4. 初始化数据库

本项目使用 ORM 模型定义了以下核心表：

- `user`
- `user_token`
- `news_category`
- `news`
- `favorite`
- `history`

你可以任选一种方式初始化：

1. 手工执行 SQL 建表
2. 基于 SQLAlchemy/Alembic 生成迁移（推荐在团队协作中使用）

> 项目目前未内置 Alembic 配置文件，建议后续补充迁移体系。

### 5. 运行服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- Swagger 文档：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- 健康入口：`GET http://127.0.0.1:8000/`

## 认证说明

登录/注册成功后会返回 `token`。需要鉴权的接口请在请求头中携带：

```http
Authorization: Bearer <token>
```

Token 相关逻辑：

- 存储表：`user_token`
- 有效期：7 天（见 `crud/users.py`）

## 主要接口

### 用户模块 `/api/user`

- `POST /register`：注册
- `POST /login`：登录
- `GET /info`：获取当前用户信息（需鉴权）
- `PUT /update`：更新用户资料（需鉴权）
- `PUT /password`：修改密码（需鉴权）

### 新闻模块 `/api/news`

- `GET /categories`：新闻分类
- `GET /list`：分类新闻分页列表
  - 参数：`categoryId`, `page`, `pageSize`
- `GET /detail`：新闻详情
  - 参数：`id`

### 收藏模块 `/api/favorite`（均需鉴权）

- `GET /check`：检查是否已收藏（`newsId`）
- `POST /add`：新增收藏
- `DELETE /remove`：取消收藏（`newsId`）
- `GET /list`：收藏分页列表（`page`, `pageSize`）
- `DELETE /clear`：清空收藏

### 历史模块 `/api/history`（均需鉴权）

- `POST /add`：新增/更新浏览历史
- `GET /list`：浏览历史分页列表（`page`, `pageSize`）
- `DELETE /delete/{history_id}`：删除单条历史
- `DELETE /clear`：清空历史

## 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

异常场景统一返回对应 `code` 与 `message`，并在调试模式下可能包含详细错误信息。

## 缓存策略（当前实现）

- 新闻分类缓存键：`news:categories`
- 新闻列表缓存键：`news:list:{category}:{page}:{pageSize}`
- 默认过期：
  - 分类：3600 秒
  - 列表：600 秒

## 开发建议

- 增加 `.env` 配置，避免将数据库密码硬编码在仓库中
- 后续可补充 `pyproject.toml`，进一步规范依赖与构建配置
- 引入 Alembic 做数据库迁移
- 补充单元测试与接口集成测试（如 `pytest + httpx`）
- 使用 JWT 替代随机 token（可选）

