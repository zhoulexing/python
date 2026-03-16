"""数据模型与异常定义"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import hashlib


# ──────────────────────────── 异常 ────────────────────────────


class YzDocErrorCode(Enum):
    """错误码定义  格式: (错误码, 错误信息)"""

    UNSUPPORTED_FILE_TYPE_ERROR = (20000001, "不支持的文件类型")
    REMOTE_EXCEL_FILES_NOT_SUPPORTED = (20000002, "远程Excel文件不支持")
    FAILED_TO_LOAD_MARKDOWN_FILE = (20000003, "加载Markdown文件失败")
    FAILED_TO_LOAD_TEXT_FILE = (20000004, "加载文本文件失败")
    FAILED_TO_LOAD_WEB_PAGE = (20000005, "加载网页失败")
    FAILED_TO_LOAD_EXCEL_FILE = (20000006, "加载Excel文件失败")
    INVALID_SPLITTER_CLASS = (20000008, "无效的切分器类")
    SPLITTER_NOT_FOUND = (20000009, "切分器未找到")
    DOCUMENT_CONTENT_EMPTY = (20000010, "文档内容为空")
    DOCUMENT_DOC_ID_MISSING = (20000011, "文档ID缺失")
    MARKDOWN_HEADER_TEXT_SPLITTER_NOT_AVAILABLE = (20000012, "MarkdownHeaderTextSplitter未找到")
    FAILED_TO_SPLIT_DOCUMENT = (20000013, "切分文档失败")
    RECURSIVE_CHARACTER_TEXT_SPLITTER_NOT_AVAILABLE = (20000014, "RecursiveCharacterTextSplitter未找到")
    FAILED_TO_OBTAIN_ACCESS_TOKEN = (20000015, "飞书获取访问令牌失败")
    FAILED_TO_GET_WIKI_OBJ_TOKEN = (20000016, "飞书获取Wiki文档对象token失败")
    DOCUMENT_NOT_AUTHORIZED = (20000017, "文档未授权")
    FAILED_TO_GET_DOCUMENT = (20000018, "飞书获取文档失败")
    FAILED_TO_GET_BLOCKS = (20000019, "飞书获取文档块失败")
    FILE_NOT_FOUND = (20000020, "文件不存在")
    FILE_SIZE_EXCEEDS_MAXIMUM_ALLOWED_SIZE = (20000021, "文件大小超过最大允许大小")
    NOT_IMPLEMENTED = (20000022, "未实现")
    FAILED_TO_GET_UPLOAD_TOKEN = (20000023, "无法从响应中提取token")
    FEISHU_CONFIG_NOT_SET = (20000024, "飞书相关参数未配置")
    CDN_CONFIG_NOT_SET = (20000025, "CDN配置未设置")
    UNSUPPORTED_CDN_PROVIDER = (20000026, "不支持的CDN提供商")
    FAILED_TO_LOAD_FEISHU_DOCUMENT = (20000027, "加载飞书文档失败")
    UNSUPPORTED_FEISHU_URL_FORMAT = (20000028, "不支持的飞书URL格式")
    CDN_CONFIG_MISSING_OPERATOR_ID = (20000029, "CDN配置缺少operator_id参数")
    CDN_CONFIG_MISSING_PROXY_DOMAIN = (20000030, "CDN配置缺少proxy_domain参数")
    UPLOAD_RESULT_MISSING_KEY = (20000031, "上传结果中缺少key字段")
    FAILED_TO_UPLOAD_IMAGE_TO_QINIU = (20000032, "上传图片到七牛云失败")
    FAILED_TO_CALL_AIGC_API = (20000033, "调用AIGC解析API失败")
    AIGC_API_PARSE_ERROR = (20000034, "AIGC API返回错误")
    AIGC_API_RESPONSE_INVALID = (20000035, "AIGC API响应格式无效")
    AIGC_API_CONFIG_NOT_SET = (20000036, "AIGC API配置未设置")
    LOCAL_FILES_NOT_SUPPORTED_BY_AIGC = (20000037, "AIGC加载器不支持本地文件")
    FAILED_TO_LOAD_DOCUMENT = (20000038, "加载文档失败")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


class YzDocException(Exception):
    """YZ-Doc 异常基类"""

    def __init__(self, error_code: YzDocErrorCode, message: Optional[str] = None) -> None:
        self.code = error_code.code
        self.message = message or error_code.message
        super().__init__(self.message)


# ──────────────────────────── Document ────────────────────────────


@dataclass
class Document:
    """文档对象"""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_type: str = ""
    source: str = ""
    doc_id: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.doc_id is None:
            self.doc_id = self._generate_id()
        if self.created_at is None:
            self.created_at = datetime.now()

    def _generate_id(self) -> str:
        content_hash = hashlib.md5(
            f"{self.source}:{self.content[:100]}".encode()
        ).hexdigest()
        return f"doc_{content_hash[:16]}"

    def to_dict(self) -> Dict[str, Any]:
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
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Document(doc_id='{self.doc_id}', doc_type='{self.doc_type}', source='{self.source}', content='{preview}')"


# ──────────────────────────── Chunk ────────────────────────────


@dataclass
class Chunk:
    """文档切片对象"""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_id: Optional[str] = None
    doc_id: str = ""
    index: int = 0

    def __post_init__(self) -> None:
        if self.chunk_id is None:
            self.chunk_id = self._generate_id()

    def _generate_id(self) -> str:
        content_hash = hashlib.md5(
            f"{self.doc_id}:{self.index}:{self.content[:50]}".encode()
        ).hexdigest()
        return f"chunk_{content_hash[:16]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_id": self.doc_id,
            "index": self.index,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        return cls(
            content=data["content"],
            metadata=data.get("metadata", {}),
            chunk_id=data.get("chunk_id"),
            doc_id=data.get("doc_id", ""),
            index=data.get("index", 0),
        )

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Chunk(chunk_id='{self.chunk_id}', doc_id='{self.doc_id}', index={self.index}, content='{preview}')"
