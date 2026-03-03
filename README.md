# AI Platform

全栈应用：FastAPI 后端 + React 前端。

## 项目结构

```
├── app/                            # Python 后端
│   ├── main.py                     # FastAPI 应用入口
│   ├── controllers/                # 控制器层 (CBV)
│   ├── services/                   # 业务逻辑层
│   ├── dal/                        # 数据访问层
│   │   ├── engine.py               # SQLAlchemy 异步引擎
│   │   ├── session.py              # 会话管理 & 依赖注入
│   │   ├── models/                 # ORM 模型 (表映射)
│   │   └── repositories/           # Repository (数据库操作)
│   ├── models/                     # 数据模型
│   │   ├── bo/                     # 业务对象
│   │   └── dto/                    # 数据传输对象
│   │       ├── requests/           # 请求 DTO
│   │       └── responses/          # 响应 DTO (BaseResponse / PageResponse)
│   ├── exceptions/                 # 异常定义 & 全局处理
│   ├── middleware/                 # 中间件
│   └── utils/                      # 工具函数
│
├── frontend/                       # React 前端
│   ├── src/
│   │   ├── api/                    # API 请求封装 (axios)
│   │   ├── components/             # 公共组件
│   │   ├── hooks/                  # 自定义 Hooks
│   │   ├── layouts/                # 页面布局
│   │   ├── pages/                  # 路由页面
│   │   ├── store/                  # 状态管理
│   │   ├── types/                  # TypeScript 类型
│   │   └── utils/                  # 工具函数
│   ├── vite.config.ts              # Vite 配置 (proxy → 后端)
│   └── package.json
│
├── packages/                       # 共享包
├── tests/                          # 测试
├── scripts/                        # 运维脚本
├── config/                         # 环境配置
├── pyproject.toml                  # Python 依赖 & 包配置
└── requirements.txt
```

## 技术栈

| 层 | 技术 |
|---|------|
| 后端框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (asyncio) + aiomysql |
| 数据验证 | Pydantic v2 |
| 前端框架 | React 19 + TypeScript |
| 构建工具 | Vite |
| 样式 | Tailwind CSS |
| HTTP 客户端 | axios |
| 路由 | react-router-dom v7 |

## 快速开始

### 后端

```bash
# 安装依赖 (推荐 uv)
uv sync

# 或 pip
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000，前端通过 Vite proxy 将 `/api/*` 请求转发到后端 `localhost:8000`。

## 架构说明

### 后端分层

```
HTTP Request → Controller → Service → Repository → Database
                  ↓             ↓          ↓
               Request DTO    BO/PO    ORM Model
                  ↓
            BaseResponse<ResponseDTO>
```

| 层 | 职责 |
|---|------|
| **Controller** | 接收请求，参数校验，调用 Service，封装统一响应 (BaseResponse / PageResponse) |
| **Service** | 核心业务逻辑，事务管理，返回 PO/BO 对象 |
| **Repository** | 数据库 CRUD 操作，封装 SQLAlchemy 查询 |
| **ORM Model** | `dal/models/` 下的 SQLAlchemy 表映射 |
| **DTO** | `models/dto/` 下的请求/响应数据结构 (Pydantic) |
| **BO** | `models/bo/` 下的业务聚合对象 (可选，用于复杂场景) |

### 统一响应格式

```json
{
  "success": true,
  "code": 200,
  "msg": "查询成功",
  "data": { ... }
}
```

分页响应：

```json
{
  "success": true,
  "code": 200,
  "msg": "查询成功",
  "data": {
    "pageInfo": { "page": 1, "pageSize": 20, "total": 100, "totalPages": 5 },
    "items": [ ... ]
  }
}
```

### 前端请求链路

```
页面组件 → api/xxx.ts → axios (baseURL: /api)
    → Vite proxy 去掉 /api 前缀
    → http://localhost:8000/...
```

## 开发规范

### 命名

- Python 文件/变量/函数：`snake_case`
- Python 类：`PascalCase`
- TypeScript 文件 (组件)：`PascalCase.tsx`
- TypeScript 文件 (工具)：`camelCase.ts`
- API 响应字段：`camelCase` (通过 Pydantic `serialization_alias` 转换)

### 新增模块 Checklist

1. `dal/models/` 添加 ORM Model
2. `dal/repositories/` 添加 Repository
3. `services/` 添加 Service
4. `models/dto/requests/` 添加请求 DTO
5. `models/dto/responses/` 添加响应 DTO
6. `controllers/` 添加 Controller 并在 `main.py` 注册路由
7. `frontend/src/types/` 添加 TypeScript 类型
8. `frontend/src/api/` 添加 API 调用函数
9. `frontend/src/pages/` 添加页面组件

## License

MIT
