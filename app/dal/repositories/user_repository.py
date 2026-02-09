"""
Example Repository
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dal.repositories.base import BaseRepository
from app.dal.models.user import User


class UserRepository(BaseRepository[User]):
    """User 数据仓库"""

    def __init__(self, session: AsyncSession):
        """
        初始化 User Repository

        Args:
            session: 数据库会话
        """
        super().__init__(User, session)

    async def find_by_name(self, name: str) -> Optional[User]:
        """
        根据名称查找

        Args:
            name: 名称

        Returns:
            Optional[User]: User 实例，不存在返回 None
        """
        stmt = select(User).where(User.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "id",
        desc: bool = True
    ) -> tuple[List[User], int]:
        """
        分页查询所有用户

        Args:
            page: 页码（从 1 开始）
            page_size: 每页大小
            order_by: 排序字段
            desc: 是否降序

        Returns:
            tuple[List[User], int]: (用户列表, 总记录数)
        """
        return await self.get_page(
            page=page,
            page_size=page_size,
            order_by=order_by,
            desc=desc
        )

    
