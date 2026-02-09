"""
Example 请求 DTO
"""
from pydantic import BaseModel, Field


class CreateExampleRequest(BaseModel):
    """创建 Example 请求"""
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    description: str = Field(..., min_length=1, max_length=500, description="描述")


class UpdateExampleRequest(BaseModel):
    """更新 Example 请求"""
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    description: str = Field(..., min_length=1, max_length=500, description="描述")
