"""文本切分器 - 基于LangChain RecursiveCharacterTextSplitter"""

from typing import List, Optional
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

from yz_doc.splitters.base import BaseSplitter
from yz_doc.core.document import Document
from yz_doc.core.chunk import Chunk
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


class TextSplitter(BaseSplitter):
    """递归字符切分器 - 基于LangChain"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        初始化切分器

        Args:
            chunk_size: 切片大小（字符数）
            chunk_overlap: 切片重叠大小（字符数）
            separators: 分隔符列表，None使用默认分隔符
            **kwargs: 其他配置参数
        """
        super().__init__(chunk_size, chunk_overlap, **kwargs)

        # 默认分隔符（中英文混合）
        self.separators = separators or [
            "\n\n",  # 段落分隔
            "\n",  # 行分隔
            "。",  # 中文句号
            "！",  # 中文感叹号
            "？",  # 中文问号
            ".",  # 英文句号
            "!",  # 英文感叹号
            "?",  # 英文问号
            ";",  # 分号
            "；",  # 中文分号
            " ",  # 空格
            "",  # 字符级别
        ]

        self._init_splitter()

    def _init_splitter(self) -> None:
        """初始化LangChain切分器"""
        try:
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.separators,
                length_function=len,
                is_separator_regex=False,
            )
        except ImportError:
            raise YzDocException(YzDocErrorCode.RECURSIVE_CHARACTER_TEXT_SPLITTER_NOT_AVAILABLE,
                "RecursiveCharacterTextSplitter not available. Install with: pip install langchain-text-splitters")

    def split(self, document: Document) -> List[Chunk]:
        """
        切分文档

        Args:
            document: Document对象

        Returns:
            Chunk对象列表

        Raises:
            SplitterError: 切分失败
        """
        # 验证文档
        self._validate_document(document)

        try:
            # 使用LangChain切分
            texts = self.splitter.split_text(document.content)

            # 创建Chunk对象列表
            chunks = []
            for i, text in enumerate(texts):
                # 合并元数据
                chunk_metadata = {
                    **document.metadata,
                    "chunk_index": i,
                    "total_chunks": len(texts),
                    "chunk_size": len(text),
                    "splitter": "text",
                }

                chunk = self._create_chunk(
                    content=text,
                    doc_id=document.doc_id or "",
                    index=i,
                    metadata=chunk_metadata,
                )
                chunks.append(chunk)

            return chunks

        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_SPLIT_DOCUMENT,
                f"Failed to split document: {str(e)}") from e

    def split_text(self, text: str) -> List[str]:
        """
        直接切分文本（不创建Chunk对象）

        Args:
            text: 文本内容

        Returns:
            文本片段列表
        """
        return self.splitter.split_text(text)
