"""Markdown 切分器 - 按标题层级切分"""

from typing import List, Tuple, Optional

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from . import BaseSplitter
from ..models import Document, Chunk, YzDocErrorCode, YzDocException


class MarkdownSplitter(BaseSplitter):
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        headers_to_split_on: Optional[List[Tuple[str, str]]] = None,
        **kwargs,
    ):
        super().__init__(chunk_size, chunk_overlap, **kwargs)
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on, strip_headers=False
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

    def split(self, document: Document) -> List[Chunk]:
        self._validate_document(document)
        try:
            md_splits = self.header_splitter.split_text(document.content)
            all_chunks = []
            idx = 0

            for split in md_splits:
                if hasattr(split, "page_content"):
                    content = split.page_content
                    split_meta = split.metadata if hasattr(split, "metadata") else {}
                elif isinstance(split, dict):
                    content = split.get("page_content", "")
                    split_meta = split.get("metadata", {})
                else:
                    content = str(split)
                    split_meta = {}

                if len(content) > self.chunk_size:
                    for sub in self.text_splitter.split_text(content):
                        meta = {**document.metadata, **split_meta, "chunk_index": idx, "splitter": "markdown", "is_sub_chunk": True}
                        all_chunks.append(self._create_chunk(sub, document.doc_id or "", idx, meta))
                        idx += 1
                else:
                    meta = {**document.metadata, **split_meta, "chunk_index": idx, "splitter": "markdown", "is_sub_chunk": False}
                    all_chunks.append(self._create_chunk(content, document.doc_id or "", idx, meta))
                    idx += 1

            for c in all_chunks:
                c.metadata["total_chunks"] = len(all_chunks)
            return all_chunks
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_SPLIT_DOCUMENT, f"Failed to split markdown: {e}") from e

    def split_text(self, text: str) -> List[str]:
        texts = []
        for split in self.header_splitter.split_text(text):
            content = getattr(split, "page_content", None) or (split.get("page_content", "") if isinstance(split, dict) else str(split))
            if len(content) > self.chunk_size:
                texts.extend(self.text_splitter.split_text(content))
            else:
                texts.append(content)
        return texts
