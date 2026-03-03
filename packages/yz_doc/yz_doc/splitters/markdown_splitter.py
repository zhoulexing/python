"""Markdown切分器 - 按标题层级切分"""

from typing import List, Tuple, Optional
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from yz_doc.splitters.base import BaseSplitter
from yz_doc.core.document import Document
from yz_doc.core.chunk import Chunk
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


class MarkdownSplitter(BaseSplitter):
    """Markdown切分器 - 按标题层级切分，保留标题结构信息"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        headers_to_split_on: Optional[List[Tuple[str, str]]] = None,
        **kwargs,
    ):
        """
        初始化切分器

        Args:
            chunk_size: 切片大小（字符数）
            chunk_overlap: 切片重叠大小（字符数）
            headers_to_split_on: 要切分的标题列表，格式: [(标记, 名称)]
                默认: [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
            **kwargs: 其他配置参数
        """
        super().__init__(chunk_size, chunk_overlap, **kwargs)

        # 默认按H1、H2、H3切分
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        self._init_splitter()

    def _init_splitter(self) -> None:
        """初始化LangChain Markdown切分器"""
        try:
            # 标题切分器
            self.header_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=self.headers_to_split_on,
                strip_headers=False,  # 保留标题
            )

            # 文本切分器（用于切分过大的段落）
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

        except ImportError:
            raise YzDocException(YzDocErrorCode.MARKDOWN_HEADER_TEXT_SPLITTER_NOT_AVAILABLE,
                "MarkdownHeaderTextSplitter not available. Install with: pip install langchain-text-splitters")

    def split(self, document: Document) -> List[Chunk]:
        """
        切分Markdown文档

        Args:
            document: Document对象

        Returns:
            Chunk对象列表

        Raises:
            YzDocException: 切分失败
        """
        # 验证文档
        self._validate_document(document)

        try:
            # 第一步：按标题切分
            md_header_splits = self.header_splitter.split_text(
                document.content)

            # 第二步：对过大的段落进行二次切分
            all_chunks = []
            chunk_index = 0

            for split in md_header_splits:
                # 提取内容和元数据
                if hasattr(split, "page_content"):
                    content = split.page_content
                    split_metadata = split.metadata if hasattr(
                        split, "metadata") else {}
                elif isinstance(split, dict):
                    content = split.get("page_content", "")
                    split_metadata = split.get("metadata", {})
                else:
                    content = str(split)
                    split_metadata = {}

                # 如果段落太大，进行二次切分
                if len(content) > self.chunk_size:
                    # 使用文本切分器
                    sub_texts = self.text_splitter.split_text(content)

                    for sub_text in sub_texts:
                        chunk_metadata = {
                            **document.metadata,
                            **split_metadata,
                            "chunk_index": chunk_index,
                            "splitter": "markdown",
                            "is_sub_chunk": True,
                        }

                        chunk = self._create_chunk(
                            content=sub_text,
                            doc_id=document.doc_id or "",
                            index=chunk_index,
                            metadata=chunk_metadata,
                        )
                        all_chunks.append(chunk)
                        chunk_index += 1
                else:
                    # 直接创建chunk
                    chunk_metadata = {
                        **document.metadata,
                        **split_metadata,
                        "chunk_index": chunk_index,
                        "splitter": "markdown",
                        "is_sub_chunk": False,
                    }

                    chunk = self._create_chunk(
                        content=content,
                        doc_id=document.doc_id or "",
                        index=chunk_index,
                        metadata=chunk_metadata,
                    )
                    all_chunks.append(chunk)
                    chunk_index += 1

            # 更新total_chunks
            for chunk in all_chunks:
                chunk.metadata["total_chunks"] = len(all_chunks)

            return all_chunks

        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_SPLIT_DOCUMENT,
                f"Failed to split markdown document: {str(e)}") from e

    def split_text(self, text: str) -> List[str]:
        """
        直接切分Markdown文本（不创建Chunk对象）

        Args:
            text: Markdown文本内容

        Returns:
            文本片段列表
        """
        md_header_splits = self.header_splitter.split_text(text)

        texts = []
        for split in md_header_splits:
            if hasattr(split, "page_content"):
                content = split.page_content
            elif isinstance(split, dict):
                content = split.get("page_content", "")
            else:
                content = str(split)

            # 如果内容过大，二次切分
            if len(content) > self.chunk_size:
                sub_texts = self.text_splitter.split_text(content)
                texts.extend(sub_texts)
            else:
                texts.append(content)

        return texts
