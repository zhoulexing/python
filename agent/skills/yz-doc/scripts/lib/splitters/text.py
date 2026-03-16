"""文本切分器"""

from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import BaseSplitter
from ..models import Document, Chunk, YzDocErrorCode, YzDocException


class TextSplitter(BaseSplitter):
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(chunk_size, chunk_overlap, **kwargs)
        self.separators = separators or [
            "\n\n", "\n",
            "。", "！", "？", ".", "!", "?", ";", "；",
            " ", "",
        ]
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False,
        )

    def split(self, document: Document) -> List[Chunk]:
        self._validate_document(document)
        try:
            texts = self.splitter.split_text(document.content)
            chunks = []
            for i, text in enumerate(texts):
                metadata = {
                    **document.metadata,
                    "chunk_index": i,
                    "total_chunks": len(texts),
                    "chunk_size": len(text),
                    "splitter": "text",
                }
                chunks.append(self._create_chunk(text, document.doc_id or "", i, metadata))
            return chunks
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_SPLIT_DOCUMENT, f"Failed to split document: {e}") from e

    def split_text(self, text: str) -> List[str]:
        return self.splitter.split_text(text)
