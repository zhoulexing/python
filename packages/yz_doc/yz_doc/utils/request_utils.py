"""请求工具函数"""

import os
from typing import Optional


# AIGC解析服务域名映射
AIGC_HOSTS = {
    "qa": "http://aigc-parser.qa.s.qima-inc.com",
    "pre": "http://aigc-parser.pre.s.qima-inc.com",
    "prod": "http://aigc-parser.prod.s.qima-inc.com",
}

# 静态代理服务域名映射
PROXY_HOSTS = {
    "qa": "http://proxy-static-qa.s.qima-inc.com",
    "pre": "http://proxy-static-pre.s.qima-inc.com",
    "prod": "http://proxy-static-prod.s.qima-inc.com",
}


def get_aigc_host(env: Optional[str] = None) -> str:
    """
    根据环境获取AIGC解析服务域名

    Args:
        env: 环境名称 (qa/pre/prod)，如果不提供则从环境变量 APPLICATION_STANDARD_ENV 获取

    Returns:
        AIGC服务域名

    Raises:
        ValueError: 不支持的环境
    """
    if env is None:
        env = os.getenv("APPLICATION_STANDARD_ENV", "qa")

    host = AIGC_HOSTS.get(env)
    if not host:
        return AIGC_HOSTS.get("qa")

    return host


def get_proxy_host(env: Optional[str] = None) -> str:
    """
    根据环境获取静态代理服务域名

    Args:
        env: 环境名称 (qa/pre/prod)，如果不提供则从环境变量 APPLICATION_STANDARD_ENV 获取

    Returns:
        静态代理服务域名

    Raises:
        ValueError: 不支持的环境
    """
    if env is None:
        env = os.getenv("APPLICATION_STANDARD_ENV", "qa")

    host = PROXY_HOSTS.get(env)
    if not host:
        return PROXY_HOSTS.get("qa")

    return host
