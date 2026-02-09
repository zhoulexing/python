"""
ORM 基类和通用 Mixin
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, func
from datetime import datetime
from typing import Any


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


class IDMixin:
    """主键 Mixin"""
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )


class TimestampMixin:
    """时间戳 Mixin"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class SoftDeleteMixin:
    """软删除 Mixin"""
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
        comment="删除时间"
    )

    @property
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.deleted_at is not None


class BaseModel(Base, IDMixin, TimestampMixin):
    """
    标准模型基类
    包含: id, created_at, updated_at
    """
    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典

        Returns:
            dict[str, Any]: 模型字典表示
        """
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
