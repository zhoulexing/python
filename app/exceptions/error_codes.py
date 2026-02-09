from enum import Enum

class BusinessErrorCode(Enum):
    """业务级别的错误码定义

    格式: (错误码, 错误信息)
    """
    BUSINESS_ERROR = (40000001, "业务错误")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]