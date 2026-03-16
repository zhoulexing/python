"""飞书文档加载器"""

import logging
import tempfile
from typing import Union, List, Optional, Tuple
from pathlib import Path

from . import BaseLoader
from ..models import Document, YzDocErrorCode, YzDocException
from ..utils.feishu_client import FeishuDocument, FeishuClient
from ..utils.qiniu import upload_image
from ..utils.env import get_proxy_host

logger = logging.getLogger(__name__)


class FeishuLoader(BaseLoader):
    SUPPORTED_TYPES = {"wiki": "feishu_wiki", "docx": "feishu_docx"}

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        download_images: bool = False,
        cdn: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy_domain = get_proxy_host()

        if not self.app_id:
            raise YzDocException(YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "飞书应用ID未配置")
        if not self.app_secret:
            raise YzDocException(YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "飞书应用密钥未配置")
        if download_images and not cdn:
            raise YzDocException(YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "CDN配置未设置,无法上传图片")
        if download_images and cdn:
            if cdn.get("operator_id") is None or cdn.get("channel") is None:
                raise YzDocException(
                    YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "CDN配置缺少operator_id或channel参数"
                )

        self.download_images = download_images
        self.cdn_config = cdn or {}
        self._feishu_client = None

    @property
    def feishu_client(self) -> FeishuClient:
        if self._feishu_client is None:
            self._feishu_client = FeishuClient(self.app_id, self.app_secret, self.proxy_domain)
        return self._feishu_client

    def load(self, source: Union[str, Path]) -> Document:
        url = str(source)
        try:
            doc_type, doc_id = self._parse_url(url)
            logger.info(f"解析飞书URL: type={doc_type}, id={doc_id}")

            if doc_type == "wiki":
                obj_token = self.feishu_client.get_wiki_obj_token(doc_id)
            else:
                obj_token = doc_id

            document = self.feishu_client.get_document(obj_token)
            blocks = self.feishu_client.get_blocks(obj_token)

            feishu_doc = FeishuDocument(document, blocks)
            markdown_content, img_tokens = feishu_doc.to_markdown()

            if self.download_images and img_tokens:
                markdown_content = self._process_images(markdown_content, img_tokens)

            metadata = {
                "loader": "feishu",
                "url": url,
                "source_type": doc_type,
                "title": document.title,
                "document_id": document.document_id,
                "image_count": len(img_tokens),
            }
            return Document(
                content=markdown_content,
                doc_type=self.SUPPORTED_TYPES[doc_type],
                source=url,
                metadata=metadata,
            )
        except PermissionError as e:
            raise YzDocException(
                YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED, f"文档授权失败: {e}"
            ) from e
        except YzDocException:
            raise
        except Exception as e:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_LOAD_FEISHU_DOCUMENT, f"加载飞书文档失败: {e}"
            ) from e

    def _parse_url(self, url: str) -> Tuple[str, str]:
        if "/wiki/" in url:
            return ("wiki", url.split("/wiki/")[1].split("?")[0])
        elif "/docx/" in url:
            return ("docx", url.split("/docx/")[1].split("?")[0])
        raise YzDocException(
            YzDocErrorCode.UNSUPPORTED_FEISHU_URL_FORMAT, f"不支持的飞书URL格式: {url}"
        )

    def _process_images(self, markdown: str, img_tokens: set) -> str:
        for img_token in img_tokens:
            try:
                img_url = self._download_and_upload_image(img_token)
                markdown = markdown.replace(f"![]({img_token})", f"![]({img_url})")
            except Exception as e:
                logger.warning(f"图片处理失败 {img_token}: {e}")
        return markdown

    def _download_and_upload_image(self, file_token: str) -> str:
        image_data = self.feishu_client.download_image(file_token)
        return self._upload_to_qiniu(image_data, file_token)

    def _upload_to_qiniu(self, image_data: bytes, file_token: str) -> str:
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
                f.write(image_data)
                temp_file = Path(f.name)

            result = upload_image(
                image_path=temp_file,
                operator_id=self.cdn_config.get("operator_id"),
                proxy_domain=self.proxy_domain,
                operator_type=self.cdn_config.get("operator_type", 1),
                channel=self.cdn_config.get("channel"),
                from_app=self.cdn_config.get("from_app"),
                max_size=self.cdn_config.get("max_size"),
            )
            return result.get("attachment_url")
        finally:
            if temp_file and temp_file.exists():
                temp_file.unlink()

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        url = str(file_path)
        return url.startswith("https://") and ("/wiki/" in url or "/docx/" in url) and "feishu.cn" in url

    def supported_types(self) -> List[str]:
        return list(self.SUPPORTED_TYPES.keys())
