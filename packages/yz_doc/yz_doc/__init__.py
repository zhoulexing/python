"""
YZ-Doc: 有赞文档处理 SDK

支持多格式文档加载与切分
"""

from typing import Union, List, Optional, Dict, Any
from pathlib import Path

from yz_doc.core.document import Document
from yz_doc.core.chunk import Chunk
from yz_doc.loaders.factory import LoaderFactory
from yz_doc.splitters.factory import SplitterFactory
from yz_doc.core.exceptions import YzDocException, YzDocErrorCode

__version__ = "0.1.2"

__all__ = [
    "YZDoc",
    "Document",
    "Chunk",
    "YzDocException",
    "YzDocErrorCode",
]


class YZDoc:
    """统一入口类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化YZDoc

        Args:
            config: 配置字典，可包含各种加载器和切分器的配置
        """
        self.config = config or {}
        self.loader_factory = LoaderFactory(self.config)
        self.splitter_factory = SplitterFactory(self.config)

    def load(
        self,
        source: Union[str, Path],
        loader_type: Optional[str] = None,
        **kwargs: Any,
    ) -> Document:
        """
        加载文档

        Args:
            source: 文件路径或URL
            loader_type: 加载器类型，None时自动检测
            **kwargs: 传递给加载器的额外参数

        Returns:
            Document对象

        Examples:
            >>> doc = YZDoc().load("path/to/file.pdf")
            >>> doc = YZDoc().load("path/to/file.docx", loader_type="langchain")
        """
        loader = self.loader_factory.get_loader(source, loader_type, **kwargs)
        return loader.load(source)

    def split(
        self,
        document: Document,
        splitter_type: str = "text",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs: Any,
    ) -> List[Chunk]:
        """
        切分文档

        Args:
            document: 文档对象
            splitter_type: 切分器类型 (text/semantic/markdown)
            chunk_size: 切片大小
            chunk_overlap: 重叠大小
            **kwargs: 传递给切分器的额外参数

        Returns:
            Chunk对象列表

        Examples:
            >>> chunks = YZDoc().split(doc, splitter_type="text", chunk_size=500)
            >>> chunks = YZDoc().split(doc, splitter_type="markdown")
        """
        splitter = self.splitter_factory.get_splitter(
            splitter_type, chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs
        )
        return splitter.split(document)

    def process(
        self,
        source: Union[str, Path],
        splitter_type: str = "text",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs: Any,
    ) -> List[Chunk]:
        """
        一站式处理：加载 + 切分

        Args:
            source: 文件路径或URL
            splitter_type: 切分器类型
            chunk_size: 切片大小
            chunk_overlap: 重叠大小
            **kwargs: 传递给加载器和切分器的额外参数

        Returns:
            Chunk对象列表

        Examples:
            >>> chunks = YZDoc().process("path/to/file.pdf", chunk_size=1000)
        """
        doc = self.load(source, **kwargs)
        return self.split(doc, splitter_type, chunk_size, chunk_overlap)
