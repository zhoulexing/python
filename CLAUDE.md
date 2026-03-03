# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

全栈 AI 平台应用：FastAPI 后端 + React 前端。

## 开发命令

### 后端 (Python)

```bash
# 安装依赖（推荐使用 uv）
uv sync

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端 (React + Vite)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端运行在 http://localhost:3000，通过 Vite proxy 将 `/api/*` 请求转发到后端。

## 架构设计

### 后端分层架构

```
HTTP Request → Controller (CBV) → Service → Repository → Database
                  ↓                  ↓          ↓
               Request DTO         PO/BO    ORM Model
                  ↓
            BaseResponse<ResponseDTO>
```

**核心层级职责：**

| 层 | 职责 |
|---|------|
| **Controller** (`app/controllers/`) | 使用 fastapi-utils 的 CBV 模式，接收请求、参数校验、调用 Service、封装统一响应 |
| **Service** (`app/services/`) | 核心业务逻辑、事务管理，返回 PO/BO 对象 |
| **Repository** (`app/dal/repositories/`) | 数据库 CRUD 操作，继承 `BaseRepository`，封装 SQLAlchemy 查询 |
| **ORM Model** (`app/dal/models/`) | SQLAlchemy 表映射，继承 `Base` |
| **DTO** (`app/models/dto/`) | 请求/响应数据结构 (Pydantic v2)，支持 `serialization_alias` 转换为 camelCase |

**关键特性：**
- 使用 `fastapi-utils` 的 `@cbv` 装饰器实现类视图控制器
- Service 通过 `@property` 懒加载，确保每个请求使用同一个 db session 实例
- 异步数据库会话通过 `get_db()` 依赖注入自动管理事务 (commit/rollback)
- 统一异常处理：`BusinessException` 通过全局 handler 转换为标准响应

**统一响应格式：**
```json
{
  "success": true,
  "code": 200,
  "msg": "查询成功",
  "data": { ... }
}
```

分页响应使用 `PageResponse.ok(items, page, page_size, total)`，自动计算总页数。

### 前端请求链路

```
页面组件 → api/xxx.ts → axios (baseURL: /api)
    → Vite proxy 去掉 /api 前缀
    → http://localhost:8000/...
```

- **Vite 配置**：`/api` 代理到 `http://localhost:8000`，自动去除前缀
- **axios 配置**：`frontend/src/api/request.ts` 响应拦截器直接返回 `res.data`
- **路径别名**：`@` 映射到 `frontend/src`

### 共享包 (packages/)

| 包 | 用途 |
|---|------|
| `yz-doc` | 文档处理 SDK，支持 PDF/OCR/Markdown/飞书/LangChain |
| `yz-dubbo` | Dubbo 服务客户端 |
| `yz-openai` | OpenAI/LiteLLM/火山引擎 API 客户端 |
| `claude-agent-sdk` | Claude Agent/MCP 工具包 |

## 开发规范

### 命名约定

- **Python**: 文件/变量/函数使用 `snake_case`，类使用 `PascalCase`
- **TypeScript**: 组件文件使用 `PascalCase.tsx`，工具文件使用 `camelCase.ts`
- **API 响应字段**: 使用 `camelCase`，通过 Pydantic `serialization_alias` 转换
- **路由**: 使用小写 + 连字符，如 `/example/user-mock`

### 新增功能模块流程

1. `app/dal/models/` - 添加 ORM Model（继承 `Base`）
2. `app/dal/repositories/` - 添加 Repository（继承 `BaseRepository[Model]`）
3. `app/services/` - 添加 Service（接收 `AsyncSession`）
4. `app/models/dto/requests/` - 添加请求 DTO
5. `app/models/dto/responses/` - 添加响应 DTO（建议添加 `from_model()` 类方法）
6. `app/controllers/` - 添加 Controller（使用 `@cbv(router)`，db 通过 `Depends(get_db)` 注入）
7. `app/main.py` - 注册路由：`app.include_router(router, prefix="/xxx")`
8. `frontend/src/types/` - 添加 TypeScript 类型
9. `frontend/src/api/` - 添加 API 调用函数
10. `frontend/src/pages/` - 添加页面组件

### 数据库配置

数据库连接信息通过环境变量配置（`app/utils/env_utils.py`）：
- `DB_Service_db_sales_ai_user`
- `DB_Service_db_sales_ai_password`
- `DB_Service_db_sales_ai_host`
- `DB_Service_db_sales_ai_port`
- `DB_Service_db_sales_ai_dbname`

异步引擎配置在 `app/dal/engine.py`，连接池大小 10，最大溢出 20。

### 异常处理

- 业务异常：抛出 `BusinessException(error_code, message)`
- 错误码定义：`app/exceptions/error_codes.py` 中的 `BusinessErrorCode` 枚举
- 全局异常处理：`app/exceptions/exception_handel.py`
- 参数校验异常：自动转换为标准响应格式

### 环境变量

- 后端：`.env` 文件（已 gitignore），使用 `python-dotenv` 加载
- 前端：`frontend/.env.development`（已提交）
