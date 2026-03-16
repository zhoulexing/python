"""AIGC 文档加载器 - PDF/Word/图片（仅 URL）"""

import logging
from typing import Union, List, Tuple, Optional
from pathlib import Path
from urllib.parse import urlparse

import httpx

from . import BaseLoader
from ..models import Document, YzDocErrorCode, YzDocException
from ..utils.env import get_aigc_host

logger = logging.getLogger(__name__)


class AIGCLoader(BaseLoader):
    SUPPORTED_TYPES = {
        ".pdf": "pdf",
        ".doc": "doc",
        ".docx": "docx",
        ".png": "image",
        ".jpeg": "image",
        ".jpg": "image",
        ".jp2": "image",
        ".webp": "image",
        ".gif": "image",
        ".bmp": "image",
    }

    def __init__(self, api_endpoint: Optional[str] = None, timeout: float = 30.0, **kwargs):
        super().__init__(**kwargs)
        if not api_endpoint:
            api_endpoint = f"{get_aigc_host()}/file_parse"
        self.api_endpoint = api_endpoint
        self.timeout = timeout

    def load(self, source: Union[str, Path]) -> Document:
        source_str = str(source)
        if not source_str.startswith(("http://", "https://")):
            raise YzDocException(
                YzDocErrorCode.LOCAL_FILES_NOT_SUPPORTED_BY_AIGC,
                f"AIGC加载器仅支持URL: {source}",
            )

        suffix = Path(urlparse(source_str).path).suffix.lower()
        if suffix not in self.SUPPORTED_TYPES:
            raise YzDocException(YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR, f"不支持的文件类型: {suffix}")

        try:
            content, backend = self._parse_file(source_str)
            return Document(
                content=content,
                doc_type=self.SUPPORTED_TYPES.get(suffix, "unknown"),
                source=source_str,
                metadata={"loader": "aigc", "url": source_str, "source_type": "remote", "backend": backend},
            )
        except YzDocException:
            raise
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_DOCUMENT, f"加载AIGC文档失败: {e}") from e

    def _parse_file(self, source: str) -> Tuple[str, str]:
        try:
            response = httpx.post(
                self.api_endpoint,
                json={"file_urls": [source]},
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            result = response.json()
            return self._extract_content(result, source)
        except httpx.TimeoutException as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_CALL_AIGC_API, f"调用AIGC API超时: {e}") from e
        except httpx.HTTPError as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_CALL_AIGC_API, f"调用AIGC API失败: {e}") from e
        except YzDocException:
            raise
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_CALL_AIGC_API, f"未知错误: {e}") from e

    def _extract_content(self, response: dict, source: str) -> Tuple[str, str]:
        if not response.get("success") or response.get("code") != 200:
            raise YzDocException(
                YzDocErrorCode.AIGC_API_PARSE_ERROR,
                f"AIGC API返回错误: {response.get('message', '未知错误')}",
            )
        data = response.get("data")
        if not data or not isinstance(data, dict):
            raise YzDocException(YzDocErrorCode.AIGC_API_RESPONSE_INVALID, "缺少data字段")

        backend = data.get("backend", "unknown")
        results = data.get("results")
        if not results or not isinstance(results, dict):
            raise YzDocException(YzDocErrorCode.AIGC_API_RESPONSE_INVALID, "缺少results字段")

        filename = Path(urlparse(source).path).stem
        if filename not in results:
            raise YzDocException(YzDocErrorCode.AIGC_API_RESPONSE_INVALID, f"未找到 '{filename}' 的解析结果")

        file_result = results[filename]
        if not isinstance(file_result, dict):
            raise YzDocException(YzDocErrorCode.AIGC_API_RESPONSE_INVALID, f"'{filename}' 结果格式无效")

        content = file_result.get("md_content")
        if content is None:
            raise YzDocException(YzDocErrorCode.AIGC_API_RESPONSE_INVALID, f"'{filename}' 缺少md_content")
        return (str(content), backend)

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        path_str = str(file_path)
        if not path_str.startswith(("http://", "https://")):
            return False
        return Path(urlparse(path_str).path).suffix.lower() in cls.SUPPORTED_TYPES

    def supported_types(self) -> List[str]:
        return list(self.SUPPORTED_TYPES.keys())
