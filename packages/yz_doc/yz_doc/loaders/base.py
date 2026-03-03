"""文档加载器基类"""

from abc import ABC, abstractmethod
from typing import Union, List, Any
from pathlib import Path

from yz_doc.core.document import Document
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


class BaseLoader(ABC):
    """文档加载器基类"""

    def __init__(self, **kwargs: Any):
        """
        初始化加载器

        Args:
            **kwargs: 加载器配置参数
        """
        self.config = kwargs

    @abstractmethod
    def load(self, source: Union[str, Path]) -> Document:
        """
        加载单个文档

        Args:
            source: 文件路径或URL

        Returns:
            Document对象

        Raises:
            YzDocException: 加载失败
        """
        pass

    def load_batch(self, sources: List[Union[str, Path]]) -> List[Document]:
        """
        批量加载文档

        Args:
            sources: 文件路径或URL列表

        Returns:
            Document对象列表
        """
        return [self.load(source) for source in sources]

    @abstractmethod
    def supported_types(self) -> List[str]:
        """
        返回支持的文件类型

        Returns:
            文件扩展名列表，如 ['.pdf', '.docx']
        """
        pass

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        """
        检查是否支持该文件类型（类方法，无需实例化）

        Args:
            file_path: 文件路径

        Returns:
            是否支持

        Note:
            子类应该重写此方法实现自己的判断逻辑
            默认实现需要实例化才能调用supported_types()，建议子类直接重写
        """
        # 默认实现：基于文件扩展名判断
        # 注意：这个默认实现有局限性，因为无法调用实例方法supported_types()
        # 建议子类重写此方法
        raise YzDocException(YzDocErrorCode.NOT_IMPLEMENTED,
                             "子类应该重写supports()方法实现自己的判断逻辑")

    def _validate_source(self, source: Union[str, Path]) -> Path:
        """
        验证数据源

        Args:
            source: 文件路径

        Returns:
            Path对象

        Raises:
            YzDocException: 文件不存在或文件类型不支持
        """
        path = Path(source)

        # 检查文件是否存在（跳过URL检查）
        if not str(source).startswith(("http://", "https://")):
            if not path.exists():
                raise YzDocException(YzDocErrorCode.FILE_NOT_FOUND,
                                     f"文件不存在: {source}")

        # 检查文件类型（调用类方法）
        if not self.__class__.supports(path):
            raise YzDocException(YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
                                  f"文件类型{path.suffix}不支持: {self.__class__.__name__}")

        return path