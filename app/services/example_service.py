"""
Example Service 业务逻辑层
"""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.dal.repositories.user_repository import UserRepository
from app.dal.models.user import User

class ExampleService:
    """User 业务逻辑服务"""

    def __init__(self, session: AsyncSession):
        """
        初始化 ExampleService

        Args:
            session: 数据库会话
        """
        self.repo = UserRepository(session)

    async def get_by_name(self, name: str) -> User:
        """
        根据名称获取 User

        Args:
            name: User 名称

        Returns:
            User: User 对象
        """
        return await self.repo.find_by_name(name)

    async def get_page(self, page: int, page_size: int) -> Tuple[List[User], int]:
        """
        分页查询 User

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[List[User], int]: (数据列表, 总记录数)
        """
        return await self.repo.get_page(page=page, page_size=page_size)
