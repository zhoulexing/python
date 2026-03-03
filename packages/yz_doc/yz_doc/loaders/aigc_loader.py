"""AIGC文档加载器 - 支持AI生成内容的加载"""

import logging
from typing import Union, List, Tuple, Optional
from pathlib import Path
from urllib.parse import urlparse

import httpx

from yz_doc.loaders.base import BaseLoader
from yz_doc.core.document import Document
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException
from yz_doc.utils.request_utils import get_aigc_host

logger = logging.getLogger(__name__)


class AIGCLoader(BaseLoader):
    """AIGC文档加载器 - 处理AI生成的内容"""

    # 支持的文档类型
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

    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        timeout: float = 30.0,
        **kwargs
    ):
        """
        初始化AIGC加载器

        Args:
            api_endpoint: AIGC API端点URL（可选）
                如果不提供，会根据环境变量 APPLICATION_STANDARD_ENV 自动选择
                支持的环境: qa, pre, prod（默认: qa）
            timeout: 请求超时时间（秒），默认30.0
            **kwargs: 其他配置参数

        Raises:
            YzDocException: API配置未设置
        """
        super().__init__(**kwargs)

        # 如果没有提供api_endpoint，根据环境变量自动选择
        if not api_endpoint:
            host = get_aigc_host()
            api_endpoint = f"{host}/file_parse"

        self.api_endpoint = api_endpoint
        self.timeout = timeout

    def load(self, source: Union[str, Path]) -> Document:
        """
        加载AIGC文档

        Args:
            source: 文件URL（仅支持URL）

        Returns:
            Document对象

        Raises:
            YzDocException: 加载失败
        """
        source_str = str(source)

        # 检查是否为URL
        if not source_str.startswith(("http://", "https://")):
            raise YzDocException(
                YzDocErrorCode.LOCAL_FILES_NOT_SUPPORTED_BY_AIGC,
                f"AIGC加载器仅支持URL，不支持本地文件: {source}"
            )

        # 验证文件类型
        path = Path(urlparse(source_str).path)
        suffix = path.suffix.lower()

        if suffix not in self.SUPPORTED_TYPES:
            raise YzDocException(
                YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
                f"不支持的文件类型: {suffix}"
            )

        try:
            # 调用AIGC API解析文件
            content, backend = self._parse_file(source_str)

            # 创建Document对象
            metadata = {
                "loader": "aigc",
                "url": source_str,
                "source_type": "remote",
                "backend": backend,
            }

            return Document(
                content=content,
                doc_type=self.SUPPORTED_TYPES.get(suffix, "unknown"),
                source=source_str,
                metadata=metadata,
            )

        except YzDocException:
            raise
        except Exception as e:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_LOAD_DOCUMENT,
                f"加载AIGC文档失败: {str(e)}"
            ) from e

    def _parse_file(self, source: str) -> Tuple[str, str]:
        """
        调用AIGC API解析文件

        Args:
            source: 文件URL

        Returns:
            (content, backend): 文件内容和后端标识

        Raises:
            YzDocException: API调用失败
        """
        try:
            # 构造请求payload
            payload = {"file_urls": [source]}

            # 发送POST请求
            response = httpx.post(
                self.api_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            # 解析JSON响应
            result = response.json()

            # 提取内容
            return self._extract_content_from_response(result, source)

        except httpx.TimeoutException as e:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_CALL_AIGC_API,
                f"调用AIGC API超时: {str(e)}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_CALL_AIGC_API,
                f"AIGC API返回HTTP错误 {e.response.status_code}: {str(e)}"
            ) from e
        except httpx.HTTPError as e:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_CALL_AIGC_API,
                f"调用AIGC API失败: {str(e)}"
            ) from e
        except Exception as e:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_CALL_AIGC_API,
                f"调用AIGC API时发生未知错误: {str(e)}"
            ) from e

    def _extract_content_from_response(
        self, response: dict, source: str
    ) -> Tuple[str, str]:
        """
        从API响应中提取文件内容

        Args:
            response: API响应JSON
            source: 原始文件URL

        Returns:
            (content, backend): 文件内容和后端标识

        Raises:
            YzDocException: 响应格式无效或解析失败
        """
        # 验证响应的success和code字段
        if not response.get("success") or response.get("code") != 200:
            message = response.get("message", "未知错误")
            raise YzDocException(
                YzDocErrorCode.AIGC_API_PARSE_ERROR,
                f"AIGC API返回错误: {message}"
            )

        # 提取data字段
        data = response.get("data")
        if not data or not isinstance(data, dict):
            raise YzDocException(
                YzDocErrorCode.AIGC_API_RESPONSE_INVALID,
                "AIGC API响应中缺少data字段或格式无效"
            )

        # 提取backend
        backend = data.get("backend", "unknown")

        # 提取results字段
        results = data.get("results")
        if not results or not isinstance(results, dict):
            raise YzDocException(
                YzDocErrorCode.AIGC_API_RESPONSE_INVALID,
                "AIGC API响应中缺少results字段或格式无效"
            )

        # 从URL中提取文件名（不含扩展名）
        filename = Path(urlparse(source).path).stem

        # 获取对应的文件内容
        if filename not in results:
            raise YzDocException(
                YzDocErrorCode.AIGC_API_RESPONSE_INVALID,
                f"AIGC API响应中未找到文件 '{filename}' 的解析结果"
            )

        file_result = results[filename]
        if not isinstance(file_result, dict):
            raise YzDocException(
                YzDocErrorCode.AIGC_API_RESPONSE_INVALID,
                f"文件 '{filename}' 的解析结果格式无效"
            )

        # 提取md_content
        content = file_result.get("md_content")
        if content is None:
            raise YzDocException(
                YzDocErrorCode.AIGC_API_RESPONSE_INVALID,
                f"文件 '{filename}' 的解析结果中缺少md_content字段"
            )

        return (str(content), backend)

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

        # 必须是URL
        if not path_str.startswith(("http://", "https://")):
            return False

        # 检查文件扩展名
        suffix = Path(urlparse(path_str).path).suffix.lower()
        return suffix in cls.SUPPORTED_TYPES

    def supported_types(self) -> List[str]:
        """
        返回支持的文件类型

        Returns:
            文件扩展名列表
        """
        return list(self.SUPPORTED_TYPES.keys())
