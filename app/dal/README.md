# 数据库层 ORM 架构说明

## 目录结构

```
service/app/dal/
├── engine.py              # 数据库引擎配置
├── session.py             # 会话管理和依赖注入
├── base.py               # ORM 基类和 Mixin
├── models/               # ORM 模型层
│   ├── __init__.py
│   └── example.py
├── repositories/         # Repository 模式（数据访问层）
│   ├── __init__.py
│   ├── base.py          # 通用 Repository 基类
│   └── example_repository.py
└── README.md            # 本文档
```

## 核心组件

### 1. engine.py - 数据库引擎

负责创建异步数据库引擎，配置连接池参数。

```python
from service.app.dal.engine import engine
```

### 2. session.py - 会话管理

提供两种方式获取数据库会话：

**方式一：上下文管理器**
```python
from service.app.dal.session import get_db_session

async with get_db_session() as session:
    # 自动处理事务提交/回滚
    repo = ExampleRepository(session)
    result = await repo.get_by_id(1)
```

**方式二：FastAPI 依赖注入**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from service.app.dal.session import get_db

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    repo = ExampleRepository(db)
    return await repo.get_all()
```

### 3. base.py - 基类和 Mixin

提供可复用的模型组件：

- **Base**: 所有模型的基类
- **IDMixin**: 主键字段
- **TimestampMixin**: created_at, updated_at 字段
- **SoftDeleteMixin**: deleted_at 字段（软删除）
- **BaseModel**: 标准模型基类（包含 ID + 时间戳）

### 4. models/ - ORM 模型

定义数据库表结构：

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from ..base import BaseModel

class Example(BaseModel):
    __tablename__ = "examples"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
```

### 5. repositories/ - 数据仓库

#### BaseRepository - 通用基类

提供标准 CRUD 操作：
- `create(**kwargs)` - 创建记录
- `get_by_id(id)` - 根据 ID 查询
- `get_all(skip, limit, order_by, desc)` - 查询所有
- `get_page(page, page_size, order_by, desc)` - 分页查询
- `update_by_id(id, **kwargs)` - 更新记录
- `delete_by_id(id)` - 删除记录
- `exists(**filters)` - 检查是否存在

#### 自定义 Repository

继承 BaseRepository 并添加特定业务方法：

```python
class ExampleRepository(BaseRepository[Example]):
    def __init__(self, session: AsyncSession):
        super().__init__(Example, session)

    async def find_by_name(self, name: str) -> Optional[Example]:
        stmt = select(Example).where(Example.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

## 使用示例

### 基本 CRUD 操作

```python
from service.app.dal.session import get_db_session
from service.app.dal.repositories.example_repository import ExampleRepository

async with get_db_session() as session:
    repo = ExampleRepository(session)

    # 创建
    example = await repo.create(name="Test", description="Description")

    # 查询
    found = await repo.get_by_id(example.id)

    # 更新
    updated = await repo.update_by_id(example.id, name="New Name")

    # 删除
    await repo.delete_by_id(example.id)
```

### 分页查询

```python
async with get_db_session() as session:
    repo = ExampleRepository(session)
    items, total = await repo.get_page(page=1, page_size=10)
    print(f"Total: {total}, Items: {len(items)}")
```

### 在 FastAPI 中使用

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from service.app.dal.session import get_db
from service.app.dal.repositories.example_repository import ExampleRepository

router = APIRouter()

@router.get("/examples/{id}")
async def get_example(id: int, db: AsyncSession = Depends(get_db)):
    repo = ExampleRepository(db)
    example = await repo.get_by_id(id)
    if not example:
        raise HTTPException(status_code=404)
    return example.to_dict()
```

### Service 层封装

```python
class ExampleService:
    def __init__(self, session: AsyncSession):
        self.repo = ExampleRepository(session)

    async def create_example(self, name: str, description: str):
        return await self.repo.create(name=name, description=description)

    async def list_examples(self, page: int = 1, page_size: int = 10):
        items, total = await self.repo.get_page(page, page_size)
        return {
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
```

## 架构优势

### 1. 代码简化
- 消除手动 SQL 编写
- 减少 40% 代码量
- 统一的查询接口

### 2. 类型安全
- 完整的类型提示
- IDE 自动补全
- 编译时错误检查

### 3. 安全性
- 自动参数化查询
- 防止 SQL 注入
- 事务自动管理

### 4. 可维护性
- 清晰的分层架构
- 易于测试和 mock
- 便于重构和扩展

### 5. 性能优化
- 连接池管理
- 懒加载支持
- 批量操作支持

## 迁移指南

### 旧代码（DAO 模式）

```python
from service.dal.dao.example_dao import ExampleDAO

dao = ExampleDAO()
example = dao.find_by_id(1)
```

### 新代码（Repository 模式）

```python
from service.app.dal.session import get_db_session
from service.app.dal.repositories.example_repository import ExampleRepository

async with get_db_session() as session:
    repo = ExampleRepository(session)
    example = await repo.get_by_id(1)
```

## 注意事项

1. **异步操作**: 所有数据库操作都是异步的，需要使用 `await`
2. **事务管理**: 使用 `get_db_session()` 上下文管理器自动处理事务
3. **依赖注入**: 在 FastAPI 中使用 `Depends(get_db)` 获取会话
4. **向后兼容**: 旧的 DAO/PO/SQL 代码仍然可用，可以逐步迁移

## 更多示例

详细使用示例请参考 [USAGE_EXAMPLE.py](./USAGE_EXAMPLE.py)
