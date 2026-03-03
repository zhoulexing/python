"""
七牛云图片上传工具

提供简单的图片上传功能
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
from yz_dubbo import invoke
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException


# 七牛云上传地址
SCHEME = "https"
QINIU_UPLOAD_HOST = "upload.qiniup.com"


# Dubbo 服务配置
DUBBO_SERVICE = "com.youzan.material.materialcenter.api.service.storage.file.StorageQiniuFileWriteService"
DUBBO_METHOD = "getPublicFileUploadToken"


def _get_upload_token(
    operator_id: int,
    operator_type: int,
    channel: str,
    from_app: str,
    max_size: int,
    **kwargs: Any
) -> str:
    """
    获取七牛云上传Token（内部方法）

    Args:
        operator_id: 操作者ID
        operator_type: 操作者类型
        channel: 业务渠道
        from_app: 来源应用
        max_size: 最大文件大小
        **kwargs: 其他参数

    Returns:
        七牛云上传Token
    """
    args = [
        {
            "channel": channel,
            "maxSize": max_size,
            "fromApp": from_app,
            "operatorType": operator_type,
            "operatorId": operator_id,
            **kwargs,
        }
    ]

    resp = invoke(
        service_name=DUBBO_SERVICE,
        method_name=DUBBO_METHOD,
        args=args,
    )

    # 根据实际响应提取 token
    if isinstance(resp, dict):
        if "data" in resp and isinstance(resp["data"], dict):
            return resp["data"].get("uploadToken", "")

    raise YzDocException(YzDocErrorCode.FAILED_TO_GET_UPLOAD_TOKEN,
                         f"无法从响应中提取token: {resp}")


def upload_image(
    image_path: Union[str, Path],
    operator_id: int,
    proxy_domain: Optional[str] = None,
    operator_type: int = 1,
    channel: str = None,
    from_app: str = None,
    max_size: int = 10240,  # 10KB
    **kwargs: Any
) -> Dict[str, Any]:
    """
    上传图片到七牛云

    Args:
        image_path: 图片路径
        operator_id: 操作者ID
        proxy_domain: 代理域名 (可选，如不提供则直接访问七牛云)
        operator_type: 操作者类型 (默认1)
        channel: 业务渠道 (默认 "ai_sales")
        from_app: 来源应用 (默认 "ai-platform")
        max_size: 最大文件大小（字节，默认10KB）
        **kwargs: 其他参数（如 operatorName, operatorKdtId, operatorPhone等）

    Returns:
        上传结果: {"key": "xxx", "hash": "xxx", ...}

    Raises:
        YzDocException: 图片不存在
        YzDocException: 上传失败

    Example:
        >>> result = upload_image("photo.jpg", operator_id=16595)
        >>> print(result['key'])

        >>> # 使用代理
        >>> result = upload_image("photo.jpg", operator_id=16595, proxy_domain="proxy.example.com")

        >>> # 自定义参数
        >>> result = upload_image(
        ...     "photo.jpg",
        ...     operator_id=16595,
        ...     channel="user_profile",
        ...     max_size=1048576,  # 1MB
        ...     operatorName="张三",
        ...     operatorKdtId=55
        ... )
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise YzDocException(YzDocErrorCode.FILE_NOT_FOUND,
                             f"图片不存在: {image_path}")

    # 1. 获取上传token
    token = _get_upload_token(
        operator_id=operator_id,
        operator_type=operator_type,
        channel=channel,
        from_app=from_app,
        max_size=max_size,
        **kwargs
    )

    # 2. 构建请求URL和Headers
    headers = {
        "scheme": SCHEME,
        "Host": QINIU_UPLOAD_HOST,
        "yzc-connect-timeout": "4000",
        "yzc-send-timeout": "200000",
        "yzc-read-timeout": "200000",
    }

    # 3. 上传图片
    with httpx.Client(timeout=30.0) as client:
        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f)}
            data = {"token": token}

            response = client.post(
                proxy_domain, files=files, data=data, headers=headers)

            if response.status_code != 200:
                raise YzDocException(YzDocErrorCode.FAILED_TO_UPLOAD_IMAGE_TO_QINIU,
                                     f"上传失败 [HTTP {response.status_code}]: {response.text}")

            result = response.json()

            # 提取实际数据
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result


def upload_images_batch(
    image_paths: List[Union[str, Path]],
    operator_id: int,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """
    批量上传图片到七牛云

    Args:
        image_paths: 图片路径列表
        operator_id: 操作者ID
        **kwargs: 其他参数 (同upload_image)

    Returns:
        上传结果列表，每个元素对应一个图片的上传结果
        成功: {"key": "xxx", "hash": "xxx", ...}
        失败: {"error": "错误信息", "file": "文件路径"}
    """
    results = []

    for image_path in image_paths:
        try:
            result = upload_image(image_path, operator_id, **kwargs)
            results.append(result)
        except Exception as e:
            # 批量上传遇到错误继续处理，将错误记录到结果中
            results.append({"error": str(e), "file": str(image_path)})

    return results
