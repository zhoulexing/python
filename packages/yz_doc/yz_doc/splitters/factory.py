"""切分器工厂"""

from typing import Optional, Dict, Any

from yz_doc.splitters.base import BaseSplitter
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException
from yz_doc.splitters.text_splitter import TextSplitter
from yz_doc.splitters.markdown_splitter import MarkdownSplitter


class SplitterFactory:
    """切分器工厂类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化工厂

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self._splitters: Dict[str, type] = {}
        self._register_default_splitters()

    def _register_default_splitters(self) -> None:
        """注册默认切分器"""
        self.register_splitter("text", TextSplitter)
        self.register_splitter("markdown", MarkdownSplitter)

    def register_splitter(self, name: str, splitter_class: type) -> None:
        """
        注册切分器

        Args:
            name: 切分器名称
            splitter_class: 切分器类
        """
        if not issubclass(splitter_class, BaseSplitter):
            raise YzDocException(YzDocErrorCode.INVALID_SPLITTER_CLASS,
                f"{splitter_class} must be a subclass of BaseSplitter")
        self._splitters[name] = splitter_class

    def get_splitter(
        self,
        splitter_type: str = "text",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs: Any,
    ) -> BaseSplitter:
        """
        获取切分器实例

        Args:
            splitter_type: 切分器类型 (text/semantic/markdown)
            chunk_size: 切片大小
            chunk_overlap: 重叠大小
            **kwargs: 传递给切分器的额外参数

        Returns:
            BaseSplitter实例

        Raises:
            YzDocException: 无法找到合适的切分器
        """
        if splitter_type not in self._splitters:
            raise YzDocException(YzDocErrorCode.SPLITTER_NOT_FOUND,
                f"Splitter type '{splitter_type}' not found. Available types: {list(self._splitters.keys())}")

        splitter_class = self._splitters[splitter_type]
        splitter_config = self.config.get(splitter_type, {})

        return splitter_class(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **{**splitter_config, **kwargs},
        )

    def list_splitters(self) -> Dict[str, type]:
        """
        列出所有已注册的切分器

        Returns:
            切分器字典 {名称: 类}
        """
        return self._splitters.copy()
