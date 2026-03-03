"""配置管理"""

from typing import Dict, Any, Optional
from pathlib import Path
import os


class Config:
    """配置管理类"""

    # 默认配置
    DEFAULT_CONFIG: Dict[str, Any] = {
        # 通用配置
        "chunk_size": 1000,
        "chunk_overlap": 200,
        # 飞书配置
        "feishu": {
            "app_id": "",
            "app_secret": "",
            "proxy_domain": "",
            "download_images": False,
        },
        # LangChain配置
        "langchain": {
            "mode": "elements",  # single/elements/paged
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化配置

        Args:
            config: 用户配置
        """
        self._config = self.DEFAULT_CONFIG.copy()
        # 从环境变量加载配置
        self._load_from_env()
        # 用户配置
        if config:
            self._config.update(config)

    def _load_from_env(self) -> None:
        """从环境变量加载配置"""
        # 飞书配置
        if os.getenv("FEISHU_APP_ID"):
            self._config["feishu"]["app_id"] = os.getenv("FEISHU_APP_ID", "")
        if os.getenv("FEISHU_APP_SECRET"):
            self._config["feishu"]["app_secret"] = os.getenv(
                "FEISHU_APP_SECRET", "")
        if os.getenv("FEISHU_PROXY_DOMAIN"):
            self._config["feishu"]["proxy_domain"] = os.getenv(
                "FEISHU_PROXY_DOMAIN", "")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'feishu.app_id'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            配置字典
        """
        return self._config.copy()

    def update(self, config: Dict[str, Any]) -> None:
        """
        更新配置

        Args:
            config: 新配置
        """
        self._config.update(config)


# 全局默认配置实例
default_config = Config()
