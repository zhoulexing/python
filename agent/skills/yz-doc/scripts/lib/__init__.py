"""YZ-Doc 文档处理 - 自包含版本"""

from typing import Union, List, Optional, Dict, Any
from pathlib import Path

from .models import Document, Chunk, YzDocException, YzDocErrorCode
from .loaders import LoaderFactory
from .splitters import SplitterFactory

__all__ = ["YZDoc", "Document", "Chunk", "YzDocException", "YzDocErrorCode"]


class YZDoc:
    """统一入口类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.loader_factory = LoaderFactory(self.config)
        self.splitter_factory = SplitterFactory(self.config)

    def load(
        self, source: Union[str, Path], loader_type: Optional[str] = None, **kwargs: Any
    ) -> Document:
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
        doc = self.load(source, **kwargs)
        return self.split(doc, splitter_type, chunk_size, chunk_overlap)
