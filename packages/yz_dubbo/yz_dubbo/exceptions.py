"""
异常定义与错误码映射
"""
from typing import Optional
from enum import Enum

class YzDubboErrorCode(Enum):
    """Dubbo 错误码定义

    格式: (错误码, 错误信息)
    """
    NETWORK_TIMEOUT = (10000001, "网络超时")
    NETWORK_ERROR = (10000002, "网络错误")
    PARAMS_EMPTY_ERROR = (10000003, "参数不能为空")
    SERVICE_INTERFACE_ERROR = (10000004, "服务接口错误")
    
    @property
    def code(self) -> int:
        return self.value[0]
    
    @property
    def message(self) -> str:
        return self.value[1]

class YzDubboException(Exception):
    """Dubbo 调用异常基类"""

    def __init__(
        self,
        error_code: YzDubboErrorCode,
        message: Optional[str] = None,
    ) -> None:
        """
        初始化 Dubbo 异常

        Args:
            error_code: 错误码元组 (code, default_message)
            message: 自定义错误信息，如果不提供则使用默认信息
        """
        self.code = error_code.code
        self.message = message or error_code.message
        super().__init__(self.message)
