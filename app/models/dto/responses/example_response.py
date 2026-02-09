"""
Example 响应 DTO
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.dal.models.user import User


class ExampleResponse(BaseModel):
    """Example 响应"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    phone: str
    created_at: Optional[datetime] = Field(
        default=None, serialization_alias="createdAt")
    updated_at: Optional[datetime] = Field(
        default=None, serialization_alias="updatedAt")

    @classmethod
    def from_model(cls, model: User) -> "ExampleResponse":
        """从模型转换为响应"""
        return cls(
            id=model.id,
            name=model.name,
            phone=model.phone,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
