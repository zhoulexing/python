"""
Example Controller 控制器层 - CBV 版本
"""
from fastapi import Depends, Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.session import get_db
from app.services.example_service import ExampleService
from app.models.dto.responses.example_response import ExampleResponse
from app.models.dto.responses.base_response import BaseResponse

router = InferringRouter()


@cbv(router)
class ExampleController:
    """Example 控制器 - 使用 CBV 模式"""

    # 依赖注入 - 类级别注入数据库会话
    db: AsyncSession = Depends(get_db)

    @property
    def service(self) -> ExampleService:
        """
        懒加载 Service 实例

        使用 @property 确保每次访问时返回同一个实例

        Returns:
            ExampleService: Example 业务逻辑服务
        """
        if not hasattr(self, '_service'):
            self._service = ExampleService(self.db)
        return self._service

    @router.get("/test/{name}", response_model=BaseResponse[ExampleResponse])
    async def get_by_name(self, name: str):
        """获取单个 User"""
        user = await self.service.get_by_name(name)
        return BaseResponse.ok(
            data=ExampleResponse.from_model(user),
            msg="查询成功"
        )

