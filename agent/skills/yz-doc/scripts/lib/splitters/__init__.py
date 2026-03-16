"""切分器：BaseSplitter + SplitterFactory"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..models import Document, Chunk, YzDocErrorCode, YzDocException


# ──────────────────────────── BaseSplitter ────────────────────────────


class BaseSplitter(ABC):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs: Any):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.config = kwargs

    @abstractmethod
    def split(self, document: Document) -> List[Chunk]:
        pass

    def split_batch(self, documents: List[Document]) -> List[List[Chunk]]:
        return [self.split(doc) for doc in documents]

    def _create_chunk(self, content: str, doc_id: str, index: int, metadata: dict) -> Chunk:
        return Chunk(content=content, metadata=metadata, doc_id=doc_id, index=index)

    def _validate_document(self, document: Document) -> None:
        if not document.content:
            raise YzDocException(YzDocErrorCode.DOCUMENT_CONTENT_EMPTY, "Document content is empty")
        if not document.doc_id:
            raise YzDocException(YzDocErrorCode.DOCUMENT_DOC_ID_MISSING, "Document doc_id is missing")


# ──────────────────────────── SplitterFactory ────────────────────────────


class SplitterFactory:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._splitters: Dict[str, type] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        from .text import TextSplitter
        from .markdown import MarkdownSplitter

        self.register("text", TextSplitter)
        self.register("markdown", MarkdownSplitter)

    def register(self, name: str, splitter_class: type) -> None:
        if not issubclass(splitter_class, BaseSplitter):
            raise YzDocException(
                YzDocErrorCode.INVALID_SPLITTER_CLASS,
                f"{splitter_class} must be a subclass of BaseSplitter",
            )
        self._splitters[name] = splitter_class

    def get_splitter(
        self, splitter_type: str = "text", chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs: Any
    ) -> BaseSplitter:
        if splitter_type not in self._splitters:
            raise YzDocException(
                YzDocErrorCode.SPLITTER_NOT_FOUND,
                f"Splitter '{splitter_type}' not found. Available: {list(self._splitters.keys())}",
            )
        cls = self._splitters[splitter_type]
        cfg = self.config.get(splitter_type, {})
        return cls(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **{**cfg, **kwargs})
