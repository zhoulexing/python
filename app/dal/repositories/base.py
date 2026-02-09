"""
通用 Repository 基类
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.dal.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    通用 Repository 基类
    提供标准 CRUD 操作
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        初始化 Repository

        Args:
            model: 模型类
            session: 数据库会话
        """
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """
        创建记录

        Args:
            **kwargs: 模型字段

        Returns:
            ModelType: 创建的模型实例
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取

        Args:
            id: 记录 ID

        Returns:
            Optional[ModelType]: 模型实例，不存在返回 None
        """
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "id",
        desc: bool = True
    ) -> List[ModelType]:
        """
        获取所有记录

        Args:
            skip: 跳过记录数
            limit: 限制记录数
            order_by: 排序字段
            desc: 是否降序

        Returns:
            List[ModelType]: 模型实例列表
        """
        stmt = select(self.model)

        # 排序
        order_column = getattr(self.model, order_by)
        stmt = stmt.order_by(order_column.desc() if desc else order_column.asc())

        # 分页
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_page(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "id",
        desc: bool = True
    ) -> tuple[List[ModelType], int]:
        """
        分页查询

        Args:
            page: 页码（从 1 开始）
            page_size: 每页大小
            order_by: 排序字段
            desc: 是否降序

        Returns:
            tuple[List[ModelType], int]: (数据列表, 总记录数)
        """
        offset = (page - 1) * page_size

        # 查询数据
        items = await self.get_all(
            skip=offset,
            limit=page_size,
            order_by=order_by,
            desc=desc
        )

        # 查询总数
        count_stmt = select(func.count()).select_from(self.model)
        total = await self.session.scalar(count_stmt)

        return items, total or 0

    async def update_by_id(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        根据 ID 更新

        Args:
            id: 记录 ID
            **kwargs: 要更新的字段

        Returns:
            Optional[ModelType]: 更新后的模型实例，不存在返回 None
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete_by_id(self, id: int) -> bool:
        """
        根据 ID 删除

        Args:
            id: 记录 ID

        Returns:
            bool: 是否删除成功
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, **filters) -> bool:
        """
        检查是否存在

        Args:
            **filters: 过滤条件

        Returns:
            bool: 是否存在
        """
        stmt = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        count = await self.session.scalar(stmt)
        return count > 0
