"""
统一响应基类
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """统一响应基类"""
    success: bool = Field(description="是否成功")
    code: int = Field(description="状态码")
    msg: Optional[str] = Field(default=None, description="提示信息")
    data: Optional[T] = Field(default=None, description="返回数据")

    @classmethod
    def ok(cls, data: Optional[T] = None, msg: str = "操作成功"):
        """成功响应"""
        return cls(success=True, code=200, msg=msg, data=data)

    @classmethod
    def error(cls, msg: str = "操作失败", code: int = 400):
        """失败响应"""
        return cls(success=False, code=code, msg=msg, data=None)


class PageInfo(BaseModel):
    """分页信息"""
    model_config = ConfigDict(populate_by_name=True)

    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量", serialization_alias="pageSize")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数", serialization_alias="totalPages")


class PageData(BaseModel, Generic[T]):
    """分页数据"""
    model_config = ConfigDict(populate_by_name=True)

    page_info: PageInfo = Field(description="分页信息", serialization_alias="pageInfo")
    items: List[T] = Field(description="分页数据")


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    success: bool = Field(description="是否成功")
    code: int = Field(description="状态码")
    msg: Optional[str] = Field(default=None, description="提示信息")
    data: PageData[T] = Field(description="分页数据")

    @classmethod
    def ok(cls, items: List[T], page: int, page_size: int, total: int, msg: str = "查询成功"):
        """成功响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            success=True,
            code=200,
            msg=msg,
            data=PageData(
                page_info=PageInfo(
                    page=page,
                    page_size=page_size,
                    total=total,
                    total_pages=total_pages
                ),
                items=items
            )
        )
