"""文档切片对象"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import hashlib


@dataclass
class Chunk:
    """文档切片对象"""

    content: str  # 切片内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据（包含位置、页码等）
    chunk_id: Optional[str] = None  # 切片唯一ID
    doc_id: str = ""  # 所属文档ID
    index: int = 0  # 在文档中的索引

    def __post_init__(self) -> None:
        """初始化后处理"""
        if self.chunk_id is None:
            self.chunk_id = self._generate_id()

    def _generate_id(self) -> str:
        """生成切片唯一ID"""
        content_hash = hashlib.md5(
            f"{self.doc_id}:{self.index}:{self.content[:50]}".encode()
        ).hexdigest()
        return f"chunk_{content_hash[:16]}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_id": self.doc_id,
            "index": self.index,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        """从字典创建Chunk对象"""
        return cls(
            content=data["content"],
            metadata=data.get("metadata", {}),
            chunk_id=data.get("chunk_id"),
            doc_id=data.get("doc_id", ""),
            index=data.get("index", 0),
        )

    def __repr__(self) -> str:
        """字符串表示"""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return (
            f"Chunk(chunk_id='{self.chunk_id}', "
            f"doc_id='{self.doc_id}', "
            f"index={self.index}, "
            f"content='{content_preview}')"
        )
