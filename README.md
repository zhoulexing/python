# AI Platform - 服务端

基于 FastAPI 的分层架构后端服务。

## 项目结构

```
service/
├── __init__.py
├── main.py                      # FastAPI 应用入口

├── controllers/                 # 控制器层 - 处理HTTP请求
│   ├── __init__.py
│   ├── example_controller.py
│   └── base_controller.py       # 控制器基类
├── services/                    # 业务逻辑层
│   ├── __init__.py
│   ├── example_service.py
│   └── base_service.py          # 服务基类
├── dal/                         # 数据访问层 (Data Access Layer)
│   ├── __init__.py
│   ├── dao/                     # 数据访问对象 - 数据库操作
│   │   ├── __init__.py
│   │   ├── example_dao.py
│   │   └── base_dao.py          # DAO基类
│   ├── po/                      # 持久化对象 - 数据库表映射
│   │   ├── __init__.py
│   │   ├── example_po.py
│   │   └── base_po.py           # PO基类
│   ├── sql/                     # SQL语句构建器
│   │   ├── __init__.py
│   │   ├── example_sql.py
│   │   └── base_sql.py          # SQL基类
│   └── database.py              # 数据库连接配置 (PyMySQL)
├── models/                      # 模型层
│   ├── __init__.py
│   ├── bo/                      # 业务对象 - Service层使用
│   │   ├── __init__.py
│   │   ├── example_bo.py
│   │   └── base_bo.py           # BO基类
│   └── dto/                     # 数据传输对象
│       ├── __init__.py
│       ├── requests/            # 请求DTO
│       │   ├── __init__.py
│       │   └── ExampleRequest.py
│       └── responses/           # 响应DTO
│           ├── __init__.py
│           ├── ExampleResponse.py
│           ├── BaseResponse.py     # 统一响应基类
│           └── PageResponse.py     # 分页响应
├── dependencies/                # 依赖注入
│   ├── __init__.py
│   └── database.py              # 数据库依赖
├── middleware/                  # 中间件
│   ├── __init__.py
│   └── error_handler.py
├── utils/                       # 工具类
│   ├── __init__.py
│   └── logger.py
├── exceptions/                  # 自定义异常
│   ├── __init__.py
│   └── business_exception.py
├── requirements.txt             # 依赖列表
├── init.sql                     # 数据库初始化脚本
├── .env.example                 # 环境变量示例
├── .env                         # 环境变量(不提交)
└── README.md
```

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL + PyMySQL
- **数据验证**: Pydantic
- **服务器**: Uvicorn

## 快速开始

### 1. 安装依赖

```bash
cd service
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

### 3. 初始化数据库

**推荐方式：使用初始化脚本**

```bash
# 确保已配置 .env 文件中的数据库信息
cd ..
./scripts/init_db.sh
```

脚本会自动：
- 读取 .env 配置
- 测试数据库连接
- 创建数据库（如果不存在）
- 创建表结构
- 插入示例数据
- 验证初始化结果

**手动方式：**

```bash
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source service/init.sql

# 或者
mysql -u root -p < service/init.sql
```

### 4. 启动服务

**推荐方式：使用启动脚本**

```bash
# 开发环境（启用热重载，单进程）
cd ..
./scripts/startup.sh

# 或设置环境变量
APPLICATION_STANDARD_ENV=dev ./scripts/startup.sh

# 生产环境（多进程，根据CPU核心数自动设置）
APPLICATION_STANDARD_ENV=prod ./scripts/startup.sh

# 自定义端口
PORT=8080 ./scripts/startup.sh
```

**其他方式：直接使用 uvicorn**

```bash
# 开发环境
uvicorn service.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn service.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 示例

### 创建数据

```bash
curl -X POST "http://localhost:8000/api/examples/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示例名称",
    "description": "示例描述"
  }'
```

### 查询数据

```bash
# 获取单条
curl "http://localhost:8000/api/examples/1"

# 分页查询
curl "http://localhost:8000/api/examples/?page=1&page_size=20"
```

### 更新数据

```bash
curl -X PUT "http://localhost:8000/api/examples/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的名称",
    "description": "更新后的描述"
  }'
```

### 删除数据

```bash
curl -X DELETE "http://localhost:8000/api/examples/1"
```

---

## 服务端规范 (Service - Python/FastAPI)

### 1.1 命名规范

#### 1.1.1 文件命名
- 所有Python文件使用 **snake_case** 命名
- 控制器文件: `{模块名}_controller.py` (例: `user_controller.py`)
- 服务文件: `{模块名}_service.py` (例: `user_service.py`)
- DAO文件: `{模块名}_dao.py` (例: `user_dao.py`)
- PO文件: `{模块名}_po.py` (例: `user_po.py`)
- SQL文件: `{模块名}_sql.py` (例: `user_sql.py`)
- BO文件: `{模块名}_bo.py` (例: `user_bo.py`)
- DTO文件: `{模块名首字母大写}{类型首字母大写}.py` (例: `UserRequest.py`, `UserResponse.py`)

#### 1.1.2 类命名
- 使用 **PascalCase** 命名
- 控制器类: `{模块名}Controller` (例: `UserController`)
- 服务类: `{模块名}Service` (例: `UserService`)
- DAO类: `{模块名}DAO` (例: `UserDAO`)
- PO类: `{模块名}PO` (例: `UserPO`)
- SQL类: `{模块名}SQL` (例: `UserSQL`)
- BO类: `{模块名}BO` (例: `UserBO`)
- DTO类:
  - 请求: `{功能名}Request` (例: `CreateUserRequest`)
  - 响应: `{功能名}Response` (例: `UserDetailResponse`)

#### 1.1.3 函数/方法命名
- 使用 **snake_case** 命名
- 控制器方法: HTTP动作相关 (例: `get_user`, `create_user`, `update_user`, `delete_user`)
- 服务方法: 业务动作相关 (例: `get_user_by_id`, `create_new_user`, `authenticate_user`)
- DAO方法: 数据操作相关 (例: `find_by_id`, `find_all`, `insert`, `update`, `delete`)
- SQL方法: SQL构建相关 (例: `build_select`, `build_insert`, `build_update`)

#### 1.1.4 变量命名
- 使用 **snake_case** 命名
- 常量使用 **UPPER_SNAKE_CASE** (例: `MAX_PAGE_SIZE`, `DEFAULT_TIMEOUT`)
- 私有变量/方法使用前缀 `_` (例: `_internal_method`)

### 1.2 层级职责

#### 1.2.1 Controller层 (控制器层)
**职责**:
- 接收HTTP请求，进行基本的参数验证
- 调用Service层执行业务逻辑
- **将Service返回的PO对象转换为Response DTO**
- 封装统一的返回数据结构（BaseResponse/PageResponse）
- 将结果转换为HTTP响应返回
- 不包含业务逻辑

**统一返回格式**:
```python
# service/models/dto/responses/BaseResponse.py
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一响应基类"""
    success: bool = Field(description="是否成功")
    code: int = Field(description="状态码")
    msg: Optional[str] = Field(default=None, description="提示信息")
    data: Optional[T] = Field(default=None, description="返回数据")

# service/models/dto/responses/PageResponse.py
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')

class PageInfo(BaseModel):
    """分页信息"""
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")

class PageData(BaseModel, Generic[T]):
    """分页数据"""
    page_info: PageInfo = Field(description="分页信息")
    items: List[T] = Field(description="分页数据")

class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    success: bool = Field(description="是否成功")
    code: int = Field(description="状态码")
    msg: Optional[str] = Field(default=None, description="提示信息")
    data: PageData[T] = Field(description="分页数据")
```

**示例**:
```python
# service/controllers/user_controller.py
from fastapi import APIRouter, Depends
from service.services.user_service import UserService
from service.models.dto.requests.UserRequest import CreateUserRequest
from service.models.dto.responses.UserResponse import UserResponse
from service.models.dto.responses.BaseResponse import BaseResponse, PageResponse
from service.models.dto.responses.PageResponse import PageData, PageInfo

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=BaseResponse[UserResponse])
async def create_user(
    request: CreateUserRequest,
    service: UserService = Depends()
):
    """创建用户"""
    # Service返回PO对象
    user_po = await service.create_user(request)

    # Controller负责转换为Response DTO并封装统一返回格式
    return BaseResponse(
        success=True,
        code=200,
        msg="创建成功",
        data=UserResponse.from_po(user_po)
    )

@router.get("/", response_model=PageResponse[UserResponse])
async def get_users(
    page: int = 1,
    page_size: int = 20,
    service: UserService = Depends()
):
    """获取用户列表（分页）"""
    # Service返回PO列表和总数
    users, total = await service.get_users_page(page, page_size)

    # Controller负责计算分页信息并封装响应
    total_pages = (total + page_size - 1) // page_size

    return PageResponse(
        success=True,
        code=200,
        msg="查询成功",
        data=PageData(
            page_info=PageInfo(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages
            ),
            items=[UserResponse.from_po(u) for u in users]
        )
    )

@router.get("/{user_id}", response_model=BaseResponse[UserResponse])
async def get_user(
    user_id: int,
    service: UserService = Depends()
):
    """获取单个用户"""
    user_po = await service.get_user_by_id(user_id)

    return BaseResponse(
        success=True,
        code=200,
        msg="查询成功",
        data=UserResponse.from_po(user_po)
    )
```

#### 1.2.2 Service层 (业务逻辑层)
**职责**:
- 处理核心业务逻辑
- 调用DAL层进行数据操作
- 协调多个DAO完成复杂业务
- 事务管理
- 业务规则验证
- **返回PO对象或BO对象（复杂业务数据），不依赖Response DTO**
- **简单查询返回PO，复杂业务（聚合多个数据源）返回BO**

**示例**:
```python
# service/services/user_service.py
from typing import Tuple, List
from service.dal.dao.user_dao import UserDAO
from service.dal.po.user_po import UserPO
from service.models.dto.requests.UserRequest import CreateUserRequest
from service.exceptions.business_exception import BusinessException
from service.utils.password import hash_password

class UserService:
    def __init__(self, user_dao: UserDAO = Depends()):
        self.user_dao = user_dao

    async def create_user(self, request: CreateUserRequest) -> UserPO:
        """创建用户业务逻辑"""
        # 业务验证
        existing_user = await self.user_dao.find_by_email(request.email)
        if existing_user:
            raise BusinessException("邮箱已存在")

        # 数据处理
        user_po = UserPO(
            username=request.username,
            email=request.email,
            password=hash_password(request.password)
        )

        # 调用DAO插入数据
        user_id = await self.user_dao.insert(user_po)
        user_po.id = user_id

        # 返回PO对象，由Controller层转换为Response
        return user_po

    async def get_users_page(self, page: int, page_size: int) -> Tuple[List[UserPO], int]:
        """获取用户分页数据"""
        offset = (page - 1) * page_size
        # 返回PO列表和总数，由Controller层封装分页响应
        users, total = await self.user_dao.find_page(offset, page_size)
        return users, total

    async def get_user_by_id(self, user_id: int) -> UserPO:
        """根据ID获取用户"""
        user = await self.user_dao.find_by_id(user_id)
        if not user:
            raise BusinessException("用户不存在")
        return user
```

#### 1.2.3 DAL层 (数据访问层)
**职责**:
- **PO (Persistent Object)**: 定义数据库表映射的持久化对象
- **DAO (Data Access Object)**: 封装数据库CRUD操作，使用PyMySQL
- **SQL**: 封装SQL语句构建逻辑
- 不包含业务逻辑，只负责数据持久化
- 提供统一的数据访问接口

**示例**:
```python
# service/dal/po/user_po.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class UserPO:
    """用户持久化对象"""
    username: str
    email: str
    password: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UserPO':
        """从字典创建"""
        return cls(
            id=data.get('id'),
            username=data['username'],
            email=data['email'],
            password=data['password'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

# service/dal/sql/user_sql.py
class UserSQL:
    """用户SQL语句构建器"""

    @staticmethod
    def build_insert() -> str:
        """构建插入SQL"""
        return """
            INSERT INTO users (username, email, password, created_at, updated_at)
            VALUES (%(username)s, %(email)s, %(password)s, NOW(), NOW())
        """

    @staticmethod
    def build_select_by_id() -> str:
        """构建根据ID查询SQL"""
        return """
            SELECT id, username, email, password, created_at, updated_at
            FROM users
            WHERE id = %(id)s
        """

    @staticmethod
    def build_select_by_email() -> str:
        """构建根据邮箱查询SQL"""
        return """
            SELECT id, username, email, password, created_at, updated_at
            FROM users
            WHERE email = %(email)s
        """

    @staticmethod
    def build_select_page() -> str:
        """构建分页查询SQL"""
        return """
            SELECT id, username, email, password, created_at, updated_at
            FROM users
            ORDER BY id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

    @staticmethod
    def build_count() -> str:
        """构建统计SQL"""
        return "SELECT COUNT(*) as total FROM users"

# service/dal/dao/user_dao.py
import pymysql
from typing import Optional, List, Tuple
from service.dal.po.user_po import UserPO
from service.dal.sql.user_sql import UserSQL
from service.dal.database import get_db_connection

class UserDAO:
    """用户数据访问对象"""

    def __init__(self):
        self.sql = UserSQL()

    async def insert(self, user_po: UserPO) -> int:
        """插入用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = self.sql.build_insert()
                cursor.execute(sql, {
                    'username': user_po.username,
                    'email': user_po.email,
                    'password': user_po.password
                })
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    async def find_by_id(self, user_id: int) -> Optional[UserPO]:
        """根据ID查找用户"""
        conn = get_db_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = self.sql.build_select_by_id()
                cursor.execute(sql, {'id': user_id})
                result = cursor.fetchone()
                return UserPO.from_dict(result) if result else None
        finally:
            conn.close()

    async def find_by_email(self, email: str) -> Optional[UserPO]:
        """根据邮箱查找用户"""
        conn = get_db_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = self.sql.build_select_by_email()
                cursor.execute(sql, {'email': email})
                result = cursor.fetchone()
                return UserPO.from_dict(result) if result else None
        finally:
            conn.close()

    async def find_page(self, offset: int, limit: int) -> Tuple[List[UserPO], int]:
        """分页查询用户"""
        conn = get_db_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 查询数据
                sql = self.sql.build_select_page()
                cursor.execute(sql, {'offset': offset, 'limit': limit})
                results = cursor.fetchall()
                users = [UserPO.from_dict(row) for row in results]

                # 查询总数
                count_sql = self.sql.build_count()
                cursor.execute(count_sql)
                total = cursor.fetchone()['total']

                return users, total
        finally:
            conn.close()

    async def update(self, user_po: UserPO) -> bool:
        """更新用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE users
                    SET username = %(username)s,
                        email = %(email)s,
                        updated_at = NOW()
                    WHERE id = %(id)s
                """
                cursor.execute(sql, {
                    'id': user_po.id,
                    'username': user_po.username,
                    'email': user_po.email
                })
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM users WHERE id = %(id)s"
                cursor.execute(sql, {'id': user_id})
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

# service/dal/database.py
import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ai_platform'),
        charset='utf8mb4',
        cursorclass=DictCursor
    )
```

#### 1.2.4 Models层 (模型层)
**职责**:
- **BO (Business Object)**: 业务对象，用于Service层封装复杂的业务数据
- **DTO (Data Transfer Object)**: 数据传输对象，用于Controller层与外部交互
- 不直接映射数据库表，而是根据业务需求组织数据
- BO可以包含业务逻辑方法

**使用场景**:
- **BO**: Service层返回的复杂业务对象（如聚合多个PO的数据）
- **DTO**: API请求响应数据结构

**示例**:
```python
# service/models/bo/example_bo.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ExampleBO:
    """示例业务对象"""
    id: int
    name: str
    description: str
    items: List[str]  # 关联数据列表
    created_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """业务逻辑方法"""
        return len(self.items) > 0
```

**Service层使用BO示例**:
```python
# service/services/example_service.py
from service.models.bo.example_bo import ExampleBO
from service.dal.dao.example_dao import ExampleDAO
from service.dal.dao.item_dao import ItemDAO

class ExampleService:
    def __init__(
        self,
        example_dao: ExampleDAO,
        item_dao: ItemDAO
    ):
        self.example_dao = example_dao
        self.item_dao = item_dao

    async def get_detail(self, id: int) -> ExampleBO:
        """获取详细信息（聚合多个数据源）"""
        # 获取基本信息
        example_po = await self.example_dao.find_by_id(id)
        if not example_po:
            raise BusinessException("数据不存在")

        # 获取关联数据
        items = await self.item_dao.find_by_example_id(id)

        # 组装为BO对象返回
        return ExampleBO(
            id=example_po.id,
            name=example_po.name,
            description=example_po.description,
            items=[item.name for item in items],
            created_at=example_po.created_at
        )
```

**Controller层使用BO示例**:
```python
# service/controllers/example_controller.py
@router.get("/{id}/detail", response_model=BaseResponse[ExampleDetailResponse])
async def get_detail(
    id: int,
    service: ExampleService = Depends()
):
    """获取详细信息"""
    # Service返回BO对象
    example_bo = await service.get_detail(id)

    # Controller将BO转换为Response DTO
    return BaseResponse(
        success=True,
        code=200,
        msg="查询成功",
        data=ExampleDetailResponse.from_bo(example_bo)
    )
```

#### 1.2.5 DTO层 (数据传输对象层)
**职责**:
- 定义API请求和响应的数据结构
- 使用Pydantic进行数据验证
- 与数据库模型分离，避免直接暴露内部结构
- **Response DTO提供`from_po`或`from_bo`方法用于转换**

**示例**:
```python
# service/models/dto/requests/ExampleRequest.py
from pydantic import BaseModel

class CreateExampleRequest(BaseModel):
    """创建示例请求"""
    name: str
    description: str

# service/models/dto/responses/ExampleResponse.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from service.dal.po.example_po import ExamplePO
from service.models.bo.example_bo import ExampleBO

class ExampleResponse(BaseModel):
    """示例响应"""
    id: int
    name: str
    description: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_po(cls, po: ExamplePO) -> 'ExampleResponse':
        """从PO对象转换"""
        return cls(
            id=po.id,
            name=po.name,
            description=po.description,
            created_at=po.created_at
        )

class ExampleDetailResponse(BaseModel):
    """示例详细响应"""
    id: int
    name: str
    description: str
    items: List[str]
    created_at: Optional[datetime] = None

    @classmethod
    def from_bo(cls, bo: ExampleBO) -> 'ExampleDetailResponse':
        """从BO对象转换"""
        return cls(
            id=bo.id,
            name=bo.name,
            description=bo.description,
            items=bo.items,
            created_at=bo.created_at
        )
```

#### 1.2.6 Dependencies层 (依赖注入层)
**职责**:
- 定义FastAPI的依赖项
- 提供认证、授权、数据库会话等可复用的依赖
- 统一管理横切关注点

**示例**:
```python
# service/dependencies/database.py
from fastapi import Depends
from service.dal.database import get_db_connection

async def get_db():
    """数据库连接依赖"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
```

### 1.3 代码规范

- 遵循 **PEP 8** 代码风格
- 使用类型注解 (Type Hints)
- 每个函数/方法必须有文档字符串 (Docstring)
- 使用 `black` 进行代码格式化
- 使用 `pylint` 或 `flake8` 进行代码检查
- 使用 `mypy` 进行类型检查

## 开发规范

### 关键规范

1. **分层架构**: Controller → Service → DAO
2. **数据流转**:
   - Service 返回 PO 对象
   - Controller 将 PO 转换为 Response DTO
3. **统一响应**: 使用 BaseResponse 和 PageResponse
4. **异常处理**: 使用 BusinessException

### 开发检查清单

- [ ] 代码符合PEP 8规范
- [ ] 所有函数有类型注解和文档字符串
- [ ] Controller层使用统一的BaseResponse/PageResponse返回格式
- [ ] Controller层负责将PO/BO转换为Response DTO
- [ ] Controller层不包含业务逻辑
- [ ] Service层返回PO对象（简单查询）或BO对象（复杂业务），不依赖Response DTO
- [ ] Service层实现核心业务逻辑
- [ ] 使用BO对象封装需要聚合多个数据源的复杂业务数据
- [ ] 数据访问通过DAO完成，使用PyMySQL
- [ ] PO对象正确映射数据库表结构
- [ ] SQL对象封装SQL语句构建逻辑
- [ ] Response DTO提供from_po或from_bo方法用于转换
- [ ] 异常处理完善
- [ ] 编写单元测试

## License

MIT
