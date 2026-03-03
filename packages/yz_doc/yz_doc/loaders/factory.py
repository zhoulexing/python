"""加载器工厂"""

from typing import Union, Optional, Dict, Any
from pathlib import Path

from yz_doc.loaders.langchain_loader import LangChainLoader
from yz_doc.loaders.feishu_loader import FeishuLoader
from yz_doc.loaders.aigc_loader import AIGCLoader
from yz_doc.loaders.base import BaseLoader
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


class LoaderFactory:
    """加载器工厂类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化工厂

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self._loaders: Dict[str, type] = {}
        self._loader_priorities: Dict[str, int] = {}  # 加载器优先级映射
        self._register_default_loaders()

    def _register_default_loaders(self) -> None:
        """注册默认加载器"""
        # 通用加载器，优先级低
        self.register_loader("langchain", LangChainLoader, priority=0)

        # AIGC加载器，中等优先级
        self.register_loader("aigc", AIGCLoader, priority=5)

        # 专用加载器，优先级高（飞书等专用加载器）
        self.register_loader("feishu", FeishuLoader, priority=10)

    def register_loader(self, name: str, loader_class: type, priority: int = 0) -> None:
        """
        注册加载器

        Args:
            name: 加载器名称
            loader_class: 加载器类
            priority: 优先级，数字越大优先级越高（默认0）
                     建议值：通用加载器=0，专用加载器=10，用户自定义=20
        """
        if not issubclass(loader_class, BaseLoader):
            raise ValueError(
                f"{loader_class} must be a subclass of BaseLoader")
        self._loaders[name] = loader_class
        self._loader_priorities[name] = priority

    def get_loader(
        self, source: Union[str, Path], loader_type: Optional[str] = None, **kwargs: Any
    ) -> BaseLoader:
        """
        获取加载器实例

        Args:
            source: 文件路径或URL
            loader_type: 加载器类型，None时自动检测
            **kwargs: 传递给加载器的额外参数

        Returns:
            BaseLoader实例

        Raises:
            UnsupportedFileTypeError: 无法找到合适的加载器
        """
        # 如果指定了加载器类型
        if loader_type:
            if loader_type not in self._loaders:
                raise YzDocException(
                    YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR, f"Loader type '{loader_type}' not found")
                
            loader_class = self._loaders[loader_type]
            return loader_class(**{**self.config.get(loader_type, {}), **kwargs})

        # 自动检测文件类型
        loader_class = self._detect_loader(source)
        if not loader_class:
            raise YzDocException(
                YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR, f"No suitable loader found for: {source}")

        # 获取对应的配置
        loader_name = self._get_loader_name(loader_class)
        loader_config = self.config.get(loader_name, {})

        return loader_class(**{**loader_config, **kwargs})

    def _detect_loader(self, source: Union[str, Path]) -> Optional[type]:
        """
        自动检测合适的加载器（按优先级从高到低）

        Args:
            source: 文件路径或URL

        Returns:
            加载器类，如果找不到则返回None
        """
        # 按优先级从高到低排序
        sorted_loaders = sorted(
            self._loaders.items(),
            key=lambda x: self._loader_priorities.get(x[0], 0),
            reverse=True  # 优先级高的在前
        )

        # 遍历所有已注册的加载器（优先级高的先检查）
        for name, loader_class in sorted_loaders:
            # 直接调用类方法检查是否支持（无需实例化）
            if loader_class.supports(source):
                return loader_class

        return None

    def _get_loader_name(self, loader_class: type) -> str:
        """
        获取加载器名称

        Args:
            loader_class: 加载器类

        Returns:
            加载器名称
        """
        for name, cls in self._loaders.items():
            if cls == loader_class:
                return name
        return loader_class.__name__.lower().replace("loader", "")

    def list_loaders(self) -> Dict[str, type]:
        """
        列出所有已注册的加载器

        Returns:
            加载器字典 {名称: 类}
        """
        return self._loaders.copy()

    def get_loader_priority(self, name: str) -> Optional[int]:
        """
        获取加载器的优先级

        Args:
            name: 加载器名称

        Returns:
            优先级值，如果加载器不存在则返回None
        """
        return self._loader_priorities.get(name)
