"""七牛云图片上传"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx

from .dubbo_client import invoke
from ..models import YzDocErrorCode, YzDocException

QINIU_UPLOAD_HOST = "upload.qiniup.com"

DUBBO_SERVICE = "com.youzan.material.materialcenter.api.service.storage.file.StorageQiniuFileWriteService"
DUBBO_METHOD = "getPublicFileUploadToken"


def _get_upload_token(
    operator_id: int,
    operator_type: int,
    channel: str,
    from_app: str,
    max_size: int,
    **kwargs: Any,
) -> str:
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

    resp = invoke(service_name=DUBBO_SERVICE, method_name=DUBBO_METHOD, args=args)

    if isinstance(resp, dict):
        if "data" in resp and isinstance(resp["data"], dict):
            return resp["data"].get("uploadToken", "")

    raise YzDocException(
        YzDocErrorCode.FAILED_TO_GET_UPLOAD_TOKEN, f"无法从响应中提取token: {resp}"
    )


def upload_image(
    image_path: Union[str, Path],
    operator_id: int,
    proxy_domain: Optional[str] = None,
    operator_type: int = 1,
    channel: str = None,
    from_app: str = None,
    max_size: int = 10240,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    上传图片到七牛云

    Args:
        image_path: 图片路径
        operator_id: 操作者ID
        proxy_domain: 代理域名
        operator_type: 操作者类型 (默认1)
        channel: 业务渠道
        from_app: 来源应用
        max_size: 最大文件大小（字节，默认10KB）
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise YzDocException(YzDocErrorCode.FILE_NOT_FOUND, f"图片不存在: {image_path}")

    token = _get_upload_token(
        operator_id=operator_id,
        operator_type=operator_type,
        channel=channel,
        from_app=from_app,
        max_size=max_size,
        **kwargs,
    )

    headers = {
        "scheme": "https",
        "Host": QINIU_UPLOAD_HOST,
        "yzc-connect-timeout": "4000",
        "yzc-send-timeout": "200000",
        "yzc-read-timeout": "200000",
    }

    with httpx.Client(timeout=30.0) as client:
        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f)}
            data = {"token": token}
            response = client.post(proxy_domain, files=files, data=data, headers=headers)

            if response.status_code != 200:
                raise YzDocException(
                    YzDocErrorCode.FAILED_TO_UPLOAD_IMAGE_TO_QINIU,
                    f"上传失败 [HTTP {response.status_code}]: {response.text}",
                )

            result = response.json()
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result


def upload_images_batch(
    image_paths: List[Union[str, Path]],
    operator_id: int,
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    """批量上传图片到七牛云"""
    results = []
    for image_path in image_paths:
        try:
            result = upload_image(image_path, operator_id, **kwargs)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "file": str(image_path)})
    return results
