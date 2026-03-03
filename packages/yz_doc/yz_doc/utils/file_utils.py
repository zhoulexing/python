"""文件处理工具"""
from pathlib import Path
from typing import Union, Optional
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        文件大小（字节）

    Raises:
        YzDocException: 文件不存在
    """
    path = Path(file_path)
    if not path.exists():
        raise YzDocException(YzDocErrorCode.FILE_NOT_FOUND,
                             f"文件不存在: {file_path}")
    return path.stat().st_size


def read_file_bytes(file_path: Union[str, Path], max_size: Optional[int] = None) -> bytes:
    """
    读取文件字节内容

    Args:
        file_path: 文件路径
        max_size: 最大读取字节数，None表示读取全部

    Returns:
        文件字节内容

    Raises:
        YzDocException: 文件不存在
        YzDocException: 文件过大
    """
    path = Path(file_path)
    if not path.exists():
        raise YzDocException(YzDocErrorCode.FILE_NOT_FOUND,
                             f"文件不存在: {file_path}")

    file_size = get_file_size(path)
    if max_size and file_size > max_size:
        raise YzDocException(YzDocErrorCode.FILE_SIZE_EXCEEDS_MAXIMUM_ALLOWED_SIZE,
                             f"文件大小({file_size} bytes)超过最大允许大小({max_size} bytes)"
                             )

    with open(path, "rb") as f:
        return f.read(max_size) if max_size else f.read()


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """
    确保目录存在，不存在则创建

    Args:
        dir_path: 目录路径

    Returns:
        Path对象
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_name(file_path: Union[str, Path]) -> str:
    """
    获取文件名（不含扩展名）

    Args:
        file_path: 文件路径

    Returns:
        文件名
    """
    return Path(file_path).stem


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    获取文件扩展名（含点）

    Args:
        file_path: 文件路径

    Returns:
        文件扩展名，如 '.pdf'
    """
    return Path(file_path).suffix.lower()


def is_url(source: str) -> bool:
    """
    检查是否为URL

    Args:
        source: 字符串

    Returns:
        是否为URL
    """
    return source.startswith(("http://", "https://", "ftp://"))


def normalize_path(file_path: Union[str, Path]) -> Path:
    """
    规范化路径

    Args:
        file_path: 文件路径

    Returns:
        规范化的Path对象
    """
    return Path(file_path).expanduser().resolve()
