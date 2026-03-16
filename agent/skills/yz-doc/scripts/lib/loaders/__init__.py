"""加载器：BaseLoader + LoaderFactory"""

from abc import ABC, abstractmethod
from typing import Union, List, Optional, Dict, Any
from pathlib import Path

from ..models import Document, YzDocErrorCode, YzDocException


# ──────────────────────────── BaseLoader ────────────────────────────


class BaseLoader(ABC):
    def __init__(self, **kwargs: Any):
        self.config = kwargs

    @abstractmethod
    def load(self, source: Union[str, Path]) -> Document:
        pass

    def load_batch(self, sources: List[Union[str, Path]]) -> List[Document]:
        return [self.load(s) for s in sources]

    @abstractmethod
    def supported_types(self) -> List[str]:
        pass

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        raise YzDocException(YzDocErrorCode.NOT_IMPLEMENTED, "子类应重写 supports()")

    def _validate_source(self, source: Union[str, Path]) -> Path:
        path = Path(source)
        if not str(source).startswith(("http://", "https://")):
            if not path.exists():
                raise YzDocException(YzDocErrorCode.FILE_NOT_FOUND, f"文件不存在: {source}")
        if not self.__class__.supports(path):
            raise YzDocException(
                YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
                f"文件类型{path.suffix}不支持: {self.__class__.__name__}",
            )
        return path


# ──────────────────────────── LoaderFactory ────────────────────────────


class LoaderFactory:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._loaders: Dict[str, type] = {}
        self._priorities: Dict[str, int] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        from .langchain import LangChainLoader
        from .aigc import AIGCLoader
        from .feishu import FeishuLoader

        self.register("langchain", LangChainLoader, priority=0)
        self.register("aigc", AIGCLoader, priority=5)
        self.register("feishu", FeishuLoader, priority=10)

    def register(self, name: str, loader_class: type, priority: int = 0) -> None:
        if not issubclass(loader_class, BaseLoader):
            raise ValueError(f"{loader_class} must be a subclass of BaseLoader")
        self._loaders[name] = loader_class
        self._priorities[name] = priority

    def get_loader(
        self, source: Union[str, Path], loader_type: Optional[str] = None, **kwargs: Any
    ) -> BaseLoader:
        if loader_type:
            if loader_type not in self._loaders:
                raise YzDocException(
                    YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
                    f"Loader type '{loader_type}' not found",
                )
            cls = self._loaders[loader_type]
            return cls(**{**self.config.get(loader_type, {}), **kwargs})

        cls = self._detect(source)
        if not cls:
            raise YzDocException(
                YzDocErrorCode.UNSUPPORTED_FILE_TYPE_ERROR,
                f"No suitable loader found for: {source}",
            )
        name = self._name_of(cls)
        return cls(**{**self.config.get(name, {}), **kwargs})

    def _detect(self, source: Union[str, Path]) -> Optional[type]:
        for name, cls in sorted(
            self._loaders.items(), key=lambda x: self._priorities.get(x[0], 0), reverse=True
        ):
            if cls.supports(source):
                return cls
        return None

    def _name_of(self, cls: type) -> str:
        for name, c in self._loaders.items():
            if c == cls:
                return name
        return cls.__name__.lower().replace("loader", "")
