"""LangChain文档加载器 - 支持Excel/Markdown/TXT/Web"""

from typing import Union, List
from pathlib import Path
import httpx
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    WebBaseLoader,
)

from yz_doc.loaders.base import BaseLoader
from yz_doc.core.document import Document
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


class LangChainLoader(BaseLoader):
    """基于LangChain的通用文档加载器"""

    # 支持的文件类型映射
    SUPPORTED_TYPES = {
        ".xlsx": "excel",
        ".xls": "excel",
        ".md": "markdown",
        ".markdown": "markdown",
        ".txt": "text",
        ".html": "web",
        ".htm": "web",
        "": "web",  # 无扩展名默认为网页
    }

    # 默认HTTP请求头
    DEFAULT_WEB_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, **kwargs):
        """
        初始化加载器

        Args:
            **kwargs: 配置参数
                mode: 加载模式 (single/elements/paged)，默认 'single'
                web_headers: 网页请求的自定义HTTP请求头
                bs_kwargs: BeautifulSoup解析参数
        """
        super().__init__(**kwargs)
        self.mode = kwargs.get("mode", "single")
        self.web_headers = kwargs.get("web_headers", self.DEFAULT_WEB_HEADERS)
        self.bs_kwargs = kwargs.get("bs_kwargs", {})

    def load(self, source: Union[str, Path]) -> Document:
        """
        加载文档

        Args:
            source: 文件路径或URL

        Returns:
            Document对象

        Raises:
            LoaderError: 加载失败
        """
        # 检查是否为URL
        is_url = str(source).startswith(("http://", "https://"))

        # 验证文件
        path = self._validate_source(source)
        suffix = path.suffix.lower()

        # 根据文件类型选择加载方法
        if suffix in [".xlsx", ".xls"]:
            if is_url:
                raise YzDocException(
                    YzDocErrorCode.REMOTE_EXCEL_FILES_NOT_SUPPORTED, "Remote Excel files are not supported")
            content = self._load_excel(path)

        elif suffix in [".md", ".markdown"]:
            # 传递原始source而不是path，以保留完整URL
            content = self._load_markdown(
                source if is_url else path, is_url=is_url)

        elif suffix == ".txt":
            # 传递原始source而不是path，以保留完整URL
            content = self._load_text(
                source if is_url else path, is_url=is_url)

        elif suffix in [".html", ".htm", ""] and is_url:
            # 网页类型（.html/.htm或无扩展名的URL）
            content = self._load_web(str(source))

        else:
            raise YzDocException(YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
                                    f"Unsupported file type: {suffix}")

        # 创建Document对象
        is_web = suffix in [".html", ".htm", ""] and is_url

        metadata = {
            "loader": "langchain",
            "mode": self.mode,
        }

        # 网页类型特殊处理
        if is_web:
            metadata["url"] = str(source)
            metadata["source_type"] = "web"
        else:
            metadata["file_name"] = path.name
            # 只为本地文件添加文件大小
            if not is_url:
                metadata["file_size"] = path.stat().st_size

        return Document(
            content=content,
            doc_type=self.SUPPORTED_TYPES.get(suffix, "unknown"),
            source=str(source),
            metadata=metadata,
        )

    def _load_excel(self, file_path: Path) -> str:
        """
        加载Excel文件

        Args:
            file_path: 文件路径

        Returns:
            文档内容
        """
        try:
            loader = UnstructuredExcelLoader(str(file_path), mode=self.mode)
            documents = loader.load()

            # 合并所有文档内容
            if not documents:
                return ""

            # 提取并合并内容
            contents = []
            for doc in documents:
                if hasattr(doc, "page_content"):
                    contents.append(doc.page_content)
                elif isinstance(doc, dict):
                    contents.append(doc.get("page_content", ""))

            return "\n\n".join(filter(None, contents))

        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_EXCEL_FILE,
                                 f"Failed to load Excel file: {str(e)}") from e

    def _load_markdown(self, file_path: Union[str, Path], is_url: bool = False) -> str:
        """
        加载Markdown文件

        Args:
            file_path: 文件路径或URL
            is_url: 是否为URL

        Returns:
            文档内容
        """
        try:
            # 如果是URL，先下载内容
            if is_url:
                response = httpx.get(str(file_path), timeout=30.0)
                response.raise_for_status()
                return response.text

            # 本地文件使用UnstructuredMarkdownLoader
            loader = UnstructuredMarkdownLoader(str(file_path), mode=self.mode)
            documents = loader.load()

            # 合并所有文档内容
            if not documents:
                return ""

            contents = []
            for doc in documents:
                if hasattr(doc, "page_content"):
                    contents.append(doc.page_content)
                elif isinstance(doc, dict):
                    contents.append(doc.get("page_content", ""))

            return "\n\n".join(filter(None, contents))

        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_MARKDOWN_FILE,
                                 f"Failed to load Markdown file: {str(e)}") from e

    def _load_text(self, file_path: Union[str, Path], is_url: bool = False) -> str:
        """
        加载纯文本文件

        Args:
            file_path: 文件路径或URL
            is_url: 是否为URL

        Returns:
            文档内容
        """
        try:
            # 如果是URL，先下载内容
            if is_url:
                response = httpx.get(str(file_path), timeout=30.0)
                response.raise_for_status()
                return response.text

            # 本地文件使用TextLoader
            loader = TextLoader(str(file_path))
            documents = loader.load()
            return "\n\n".join(filter(None, [doc.page_content for doc in documents]))
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_TEXT_FILE,
                                 f"Failed to load text file: {str(e)}") from e

    def _load_web(self, url: str) -> str:
        """
        加载网页内容

        Args:
            url: 网页URL

        Returns:
            网页文本内容
        """
        try:
            # 使用 WebBaseLoader 加载网页
            loader = WebBaseLoader(
                web_paths=[url],
                header_template=self.web_headers,
                bs_kwargs=self.bs_kwargs
            )
            documents = loader.load()

            # 合并所有文档内容
            if not documents:
                return ""

            contents = []
            for doc in documents:
                if hasattr(doc, "page_content"):
                    contents.append(doc.page_content)
                elif isinstance(doc, dict):
                    contents.append(doc.get("page_content", ""))

            return "\n\n".join(filter(None, contents))

        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_WEB_PAGE,
                                 f"Failed to load web page: {str(e)}") from e

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        """
        检查是否支持该文件类型（类方法）

        Args:
            file_path: 文件路径或URL

        Returns:
            是否支持
        """
        path_str = str(file_path)

        # URL类型判断
        if path_str.startswith(("http://", "https://")):
            # 网页URL（无扩展名或.html/.htm）
            suffix = Path(path_str).suffix.lower()
            return suffix in cls.SUPPORTED_TYPES

        # 本地文件判断
        suffix = Path(file_path).suffix.lower()
        return suffix in cls.SUPPORTED_TYPES

    def supported_types(self) -> List[str]:
        """
        返回支持的文件类型

        Returns:
            文件扩展名列表
        """
        return list(self.SUPPORTED_TYPES.keys())
