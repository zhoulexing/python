"""文档切分器基类"""

from abc import ABC, abstractmethod
from typing import List, Any

from yz_doc.core.document import Document
from yz_doc.core.chunk import Chunk
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException

class BaseSplitter(ABC):
    """文档切分器基类"""

    def __init__(
        self, chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs: Any
    ):
        """
        初始化切分器

        Args:
            chunk_size: 切片大小（字符数）
            chunk_overlap: 切片重叠大小（字符数）
            **kwargs: 切分器配置参数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.config = kwargs

    @abstractmethod
    def split(self, document: Document) -> List[Chunk]:
        """
        切分文档

        Args:
            document: Document对象

        Returns:
            Chunk对象列表

        Raises:
            YzDocException: 切分失败时抛出
        """
        pass

    def split_batch(self, documents: List[Document]) -> List[List[Chunk]]:
        """
        批量切分文档

        Args:
            documents: Document对象列表

        Returns:
            Chunk对象列表的列表
        """
        return [self.split(doc) for doc in documents]

    def _create_chunk(
        self, content: str, doc_id: str, index: int, metadata: dict
    ) -> Chunk:
        """
        创建Chunk对象

        Args:
            content: 切片内容
            doc_id: 文档ID
            index: 切片索引
            metadata: 元数据

        Returns:
            Chunk对象
        """
        return Chunk(
            content=content, metadata=metadata, doc_id=doc_id, index=index
        )

    def _validate_document(self, document: Document) -> None:
        """
        验证文档对象

        Args:
            document: Document对象

        Raises:
            YzDocException: 文档无效时抛出
        """
        if not document.content:
            raise YzDocException(YzDocErrorCode.DOCUMENT_CONTENT_EMPTY, "Document content is empty")

        if not document.doc_id:
            raise YzDocException(YzDocErrorCode.DOCUMENT_DOC_ID_MISSING, "Document doc_id is missing")
