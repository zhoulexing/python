"""
配置管理模块
支持多环境配置
"""

import os

env = os.getenv("APPLICATION_STANDARD_ENV", "qa")

class DubboConfig:
    """Dubbo 配置类"""

    # 环境映射表
    ENV_HOSTS = {
        "qa": "http://tether-qa.s.qima-inc.com:8680",
        "pre": "http://tether-pre.s.qima-inc.com:8680",
        "prod": "http://tether.s.qima-inc.com:8680",
    }

    def __init__(
        self,
        timeout: int = 3000,
    ) -> None:
        """
        初始化配置

        Args:
            timeout: 超时时间 (毫秒)
        """
        # 优先级: 参数 > 环境变量 > 默认值
        self.timeout = timeout

    @property
    def base_url(self) -> str:
        """获取 Tether 网关基础 URL"""
        return self.ENV_HOSTS[env]


# 全局默认配置
config = DubboConfig()
