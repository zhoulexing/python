"""文档对象模型"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib


@dataclass
class Document:
    """文档对象"""

    content: str  # 文档内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    doc_type: str = ""  # 文档类型 (pdf/docx/pptx/markdown/image/feishu等)
    source: str = ""  # 来源路径/URL
    doc_id: Optional[str] = None  # 文档唯一ID
    created_at: Optional[datetime] = None  # 创建时间

    def __post_init__(self) -> None:
        """初始化后处理"""
        if self.doc_id is None:
            # 根据source和content生成唯一ID
            self.doc_id = self._generate_id()

        if self.created_at is None:
            self.created_at = datetime.now()

    def _generate_id(self) -> str:
        """生成文档唯一ID"""
        content_hash = hashlib.md5(
            f"{self.source}:{self.content[:100]}".encode()
        ).hexdigest()
        return f"doc_{content_hash[:16]}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_type": self.doc_type,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """从字典创建Document对象"""
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            content=data["content"],
            metadata=data.get("metadata", {}),
            doc_type=data.get("doc_type", ""),
            source=data.get("source", ""),
            doc_id=data.get("doc_id"),
            created_at=created_at,
        )

    def __repr__(self) -> str:
        """字符串表示"""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return (
            f"Document(doc_id='{self.doc_id}', "
            f"doc_type='{self.doc_type}', "
            f"source='{self.source}', "
            f"content='{content_preview}')"
        )
