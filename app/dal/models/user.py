"""
User 模型
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from app.dal.base import BaseModel


class User(BaseModel):
    """用户模型"""
    __tablename__ = "user"
    __table_args__ = {
        'comment': '用户表',
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="名称"
    )
    phone: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="手机号"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, phone={self.phone})>"
