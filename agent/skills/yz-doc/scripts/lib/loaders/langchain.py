"""LangChain 文档加载器 - txt/md/xlsx/web"""

from typing import Union, List
from pathlib import Path

import httpx
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    WebBaseLoader,
)

from . import BaseLoader
from ..models import Document, YzDocErrorCode, YzDocException


class LangChainLoader(BaseLoader):
    SUPPORTED_TYPES = {
        ".xlsx": "excel",
        ".xls": "excel",
        ".md": "markdown",
        ".markdown": "markdown",
        ".txt": "text",
        ".html": "web",
        ".htm": "web",
        "": "web",
    }

    DEFAULT_WEB_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = kwargs.get("mode", "single")
        self.web_headers = kwargs.get("web_headers", self.DEFAULT_WEB_HEADERS)
        self.bs_kwargs = kwargs.get("bs_kwargs", {})

    def load(self, source: Union[str, Path]) -> Document:
        is_url = str(source).startswith(("http://", "https://"))
        path = self._validate_source(source)
        suffix = path.suffix.lower()

        if suffix in [".xlsx", ".xls"]:
            if is_url:
                raise YzDocException(YzDocErrorCode.REMOTE_EXCEL_FILES_NOT_SUPPORTED, "Remote Excel files are not supported")
            content = self._load_excel(path)
        elif suffix in [".md", ".markdown"]:
            content = self._load_markdown(source if is_url else path, is_url=is_url)
        elif suffix == ".txt":
            content = self._load_text(source if is_url else path, is_url=is_url)
        elif suffix in [".html", ".htm", ""] and is_url:
            content = self._load_web(str(source))
        else:
            raise YzDocException(YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR, f"Unsupported file type: {suffix}")

        is_web = suffix in [".html", ".htm", ""] and is_url
        metadata = {"loader": "langchain", "mode": self.mode}
        if is_web:
            metadata["url"] = str(source)
            metadata["source_type"] = "web"
        else:
            metadata["file_name"] = path.name
            if not is_url:
                metadata["file_size"] = path.stat().st_size

        return Document(content=content, doc_type=self.SUPPORTED_TYPES.get(suffix, "unknown"), source=str(source), metadata=metadata)

    def _load_excel(self, file_path: Path) -> str:
        try:
            docs = UnstructuredExcelLoader(str(file_path), mode=self.mode).load()
            return "\n\n".join(filter(None, [getattr(d, "page_content", "") for d in docs]))
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_EXCEL_FILE, f"Failed to load Excel: {e}") from e

    def _load_markdown(self, file_path: Union[str, Path], is_url: bool = False) -> str:
        try:
            if is_url:
                return httpx.get(str(file_path), timeout=30.0).text
            docs = UnstructuredMarkdownLoader(str(file_path), mode=self.mode).load()
            return "\n\n".join(filter(None, [getattr(d, "page_content", "") for d in docs]))
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_MARKDOWN_FILE, f"Failed to load Markdown: {e}") from e

    def _load_text(self, file_path: Union[str, Path], is_url: bool = False) -> str:
        try:
            if is_url:
                return httpx.get(str(file_path), timeout=30.0).text
            docs = TextLoader(str(file_path)).load()
            return "\n\n".join(filter(None, [d.page_content for d in docs]))
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_TEXT_FILE, f"Failed to load text: {e}") from e

    def _load_web(self, url: str) -> str:
        try:
            docs = WebBaseLoader(web_paths=[url], header_template=self.web_headers, bs_kwargs=self.bs_kwargs).load()
            return "\n\n".join(filter(None, [getattr(d, "page_content", "") for d in docs]))
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_WEB_PAGE, f"Failed to load web page: {e}") from e

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        path_str = str(file_path)
        if path_str.startswith(("http://", "https://")):
            return Path(path_str).suffix.lower() in cls.SUPPORTED_TYPES
        return Path(file_path).suffix.lower() in cls.SUPPORTED_TYPES

    def supported_types(self) -> List[str]:
        return list(self.SUPPORTED_TYPES.keys())
