"""
Dubbo 客户端实现 (基于 HTTP 网关)
"""
from typing import Any, Dict, List, Optional

import httpx

from .config import DubboConfig, config as default_config
from .exceptions import YzDubboException, YzDubboErrorCode


class DubboClient:
    """
    Dubbo HTTP 客户端 (单例模式)

    基于 Tether 网关进行 Dubbo 调用
    """
    def __init__(self, config: Optional[DubboConfig] = None) -> None:
        """
        初始化客户端

        Args:
            config: 配置对象 (可选,默认使用全局配置)
        """
        if hasattr(self, "_initialized"):
            return

        self.config = config or default_config
        self._http_client = httpx.Client(base_url=self.config.base_url)
        self._initialized = True

    def invoke(
        self,
        service_name: str,
        method_name: str,
        args: Optional[List[Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 3000,
    ) -> Any:
        """
        调用 Dubbo 服务

        Args:
            service_name: 服务接口名 (如 com.youzan.service.UserService)
            method_name: 方法名
            args: 参数列表
            headers: 自定义请求头
            timeout: 超时时间(毫秒,默认3000)

        Returns:
            调用结果 (直接返回响应数据)

        Raises:
            YzDubboException: 调用失败时抛出
        """
        
        if not service_name or not method_name:
            raise YzDubboException(
                YzDubboErrorCode.PARAMS_EMPTY_ERROR,
                "service_name and method_name are required",
            )
        
        try:
            # 构建请求
            url_path = f"/soa/{service_name}/{method_name}"
            request_headers = {"x-request-protocol": "dubbo", "content-type": "application/json"}
            request_headers.update(headers or {})

            # 发起请求
            response = self._http_client.post(
                url_path, json=args or [], headers=request_headers, timeout=timeout / 1000.0
            )
            
            # 检查响应
            if response.status_code != 200:
                raise YzDubboException(
                    YzDubboErrorCode.SERVICE_INTERFACE_ERROR,
                    f"HTTP {response.status_code}: {response.text}",
                )

            return response.json()

        except YzDubboException:
            raise
        except httpx.TimeoutException as e:
            raise YzDubboException(
                YzDubboErrorCode.NETWORK_TIMEOUT,
                f"Request timeout after {timeout}ms",
            ) from e
        except Exception as e:
            raise YzDubboException(
                YzDubboErrorCode.NETWORK_ERROR,
                str(e),
            ) from e

    def close(self) -> None:
        """关闭 HTTP 客户端"""
        if hasattr(self, "_http_client"):
            self._http_client.close()


# 全局默认客户端实例
_default_client = DubboClient()


def invoke(
    service_name: str,
    method_name: str,
    args: Optional[List[Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 3000,
) -> Any:
    """
    全局 invoke 函数 (推荐使用)

    Args:
        service_name: 服务接口名
        method_name: 方法名
        args: 参数列表
        headers: 自定义请求头
        timeout: 超时时间(毫秒,默认3000)

    Returns:
        调用结果 (直接返回响应数据)
    """
    return _default_client.invoke(service_name, method_name, args, headers, timeout)
