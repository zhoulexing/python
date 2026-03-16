"""Dubbo HTTP 客户端（基于 Tether 网关，合并自 yz-dubbo）"""

import os
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx


# ──────────────────────────── 异常 ────────────────────────────


class YzDubboErrorCode(Enum):
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
    def __init__(self, error_code: YzDubboErrorCode, message: Optional[str] = None) -> None:
        self.code = error_code.code
        self.message = message or error_code.message
        super().__init__(self.message)


# ──────────────────────────── 配置 ────────────────────────────


ENV_HOSTS = {
    "qa": "http://tether-qa.s.qima-inc.com:8680",
    "pre": "http://tether-pre.s.qima-inc.com:8680",
    "prod": "http://tether.s.qima-inc.com:8680",
}

_env = os.getenv("APPLICATION_STANDARD_ENV", "qa")
_base_url = ENV_HOSTS.get(_env, ENV_HOSTS["qa"])


# ──────────────────────────── 客户端 ────────────────────────────


class DubboClient:
    """Dubbo HTTP 客户端，基于 Tether 网关"""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self._base_url = base_url or _base_url
        self._http_client = httpx.Client(base_url=self._base_url)

    def invoke(
        self,
        service_name: str,
        method_name: str,
        args: Optional[List[Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 3000,
    ) -> Any:
        if not service_name or not method_name:
            raise YzDubboException(
                YzDubboErrorCode.PARAMS_EMPTY_ERROR,
                "service_name and method_name are required",
            )

        try:
            url_path = f"/soa/{service_name}/{method_name}"
            request_headers = {
                "x-request-protocol": "dubbo",
                "content-type": "application/json",
            }
            request_headers.update(headers or {})

            response = self._http_client.post(
                url_path, json=args or [], headers=request_headers, timeout=timeout / 1000.0
            )

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
                YzDubboErrorCode.NETWORK_TIMEOUT, f"Request timeout after {timeout}ms"
            ) from e
        except Exception as e:
            raise YzDubboException(YzDubboErrorCode.NETWORK_ERROR, str(e)) from e

    def close(self) -> None:
        if hasattr(self, "_http_client"):
            self._http_client.close()


# 全局默认客户端
_default_client = DubboClient()


def invoke(
    service_name: str,
    method_name: str,
    args: Optional[List[Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 3000,
) -> Any:
    """全局 invoke 快捷函数"""
    return _default_client.invoke(service_name, method_name, args, headers, timeout)
