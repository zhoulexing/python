"""飞书文档加载器"""

import logging
import tempfile
from typing import Union, List, Optional, Tuple
from pathlib import Path

from yz_doc.loaders.base import BaseLoader
from yz_doc.core.document import Document
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException
from yz_doc.utils.feishu_utils import (
    FeishuDocument,
    FeishuClient,
)
from yz_doc.utils.qiniu_utils import upload_image
from yz_doc.utils.request_utils import get_proxy_host

logger = logging.getLogger(__name__)


class FeishuLoader(BaseLoader):
    """飞书文档加载器"""

    # 支持的文档类型
    SUPPORTED_TYPES = {
        "wiki": "feishu_wiki",
        "docx": "feishu_docx",
    }

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        download_images: bool = False,
        cdn: Optional[dict] = None,
        **kwargs
    ):
        """
        初始化飞书加载器

        Args:
            app_id: 飞书应用ID,默认从环境变量FEISHU_APP_ID读取
            app_secret: 飞书应用密钥,默认从环境变量FEISHU_APP_SECRET读取
            download_images: 是否下载图片(默认False)
            cdn: CDN配置(图片上传),包含provider, bucket, access_key, secret_key
            **kwargs: 其他配置参数
        """
        super().__init__(**kwargs)

        # 飞书应用配置
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy_domain = get_proxy_host()

        if not self.app_id:
            raise YzDocException(
                YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "飞书应用ID未配置")

        if not self.app_secret:
            raise YzDocException(
                YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "飞书应用密钥未配置")

        if download_images and not cdn:
            raise YzDocException(
                YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "CDN配置未设置,无法上传图片")

        if download_images and cdn:
            if (cdn.get("operator_id") is None or cdn.get("channel") is None):
                raise YzDocException(
                    YzDocErrorCode.FEISHU_CONFIG_NOT_SET, "CDN配置缺少operator_id或channel参数")

        # 图片处理配置
        self.download_images = download_images
        self.cdn_config = cdn or {}

        # 创建飞书客户端
        self._feishu_client = None

    @property
    def feishu_client(self) -> FeishuClient:
        """获取飞书客户端(懒加载)"""
        if self._feishu_client is None:
            self._feishu_client = FeishuClient(
                self.app_id, self.app_secret, self.proxy_domain)
        return self._feishu_client

    def load(self, source: Union[str, Path]) -> Document:
        """
        加载飞书文档

        Args:
            source: 飞书文档URL

        Returns:
            Document对象

        Raises:
            YzDocException: 加载失败
        """
        url = str(source)

        try:
            # 1. 解析URL,获取文档类型和ID
            doc_type, doc_id = self._parse_url(url)
            logger.info(f"解析飞书URL: type={doc_type}, id={doc_id}")

            # 2. 如果是wiki,先获取obj_token
            if doc_type == "wiki":
                obj_token = self.feishu_client.get_wiki_obj_token(doc_id)
                logger.info(f"Wiki文档obj_token: {obj_token}")
            else:
                obj_token = doc_id

            # 3. 获取文档基础信息
            document = self.feishu_client.get_document(obj_token)
            logger.info(f"获取文档信息成功: {document.title}")

            # 4. 分页获取所有文档块
            blocks = self.feishu_client.get_blocks(obj_token)
            logger.info(f"获取文档块成功: {len(blocks)}个块")

            # 5. 转换为Markdown
            feishu_doc = FeishuDocument(document, blocks)
            markdown_content, img_tokens = feishu_doc.to_markdown()
            logger.info(f"转换为Markdown成功,内容长度: {len(markdown_content)}")

            # 6. 处理图片(如果需要)
            if self.download_images and img_tokens:
                markdown_content = self._process_images(
                    markdown_content, img_tokens)

            # 7. 创建Document对象并返回
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
            raise YzDocException(YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                                 f"文档授权失败: {str(e)}") from e
        except Exception as e:
            raise YzDocException(YzDocErrorCode.FAILED_TO_LOAD_FEISHU_DOCUMENT,
                                 f"加载飞书文档失败: {str(e)}") from e

    def _parse_url(self, url: str) -> Tuple[str, str]:
        """
        解析飞书URL

        Args:
            url: 飞书文档URL

        Returns:
            (doc_type, doc_id): 文档类型和文档ID

        Raises:
            YzDocException: URL格式不正确
        """
        if "/wiki/" in url:
            doc_id = url.split("/wiki/")[1].split("?")[0]
            return ("wiki", doc_id)
        elif "/docx/" in url:
            doc_id = url.split("/docx/")[1].split("?")[0]
            return ("docx", doc_id)
        else:
            raise YzDocException(YzDocErrorCode.UNSUPPORTED_FEISHU_URL_FORMAT,
                                 f"不支持的飞书URL格式: {url}")

    def _process_images(self, markdown: str, img_tokens: set) -> str:
        """
        处理文档中的图片

        Args:
            markdown: Markdown内容
            img_tokens: 图片token集合

        Returns:
            处理后的Markdown内容
        """
        if not img_tokens:
            return markdown

        logger.info(f"开始处理{len(img_tokens)}张图片")

        for img_token in img_tokens:
            try:
                img_url = self._download_and_upload_image(img_token)
                markdown = markdown.replace(
                    f"![]({img_token})", f"![]({img_url})")
                logger.debug(f"图片处理成功: {img_token} -> {img_url}")
            except Exception as e:
                logger.warning(f"图片处理失败 {img_token}: {e}")
                # 图片处理失败不影响主流程,保留token

        return markdown

    def _download_and_upload_image(self, file_token: str) -> str:
        """
        下载图片并上传到CDN

        Args:
            file_token: 图片文件token

        Returns:
            图片公网URL

        Raises:
            Exception: 下载或上传失败
        """
        # 1. 下载图片
        image_data = self.feishu_client.download_image(file_token)

        # 2. 上传到CDN
        return self._upload_to_qiniu(image_data, file_token)
        

    def _upload_to_qiniu(self, image_data: bytes, file_token: str) -> str:
        """
        上传图片到七牛云

        Args:
            image_data: 图片二进制数据
            file_token: 文件token(用作文件名)

        Returns:
            图片公网URL

        Raises:
            Exception: 上传失败
        """
        # 1. 创建临时文件保存图片数据
        temp_file = None
        try:
            # 使用文件token作为文件名，保留扩展名
            suffix = ".png"  # 默认使用png，实际可以根据图片类型判断
            with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as f:
                f.write(image_data)
                temp_file = Path(f.name)

            # 2. 从CDN配置中获取七牛云参数
            operator_id = self.cdn_config.get("operator_id")
            proxy_domain = self.proxy_domain

            # 3. 调用upload_image上传图片
            result = upload_image(
                image_path=temp_file,
                operator_id=operator_id,
                proxy_domain=proxy_domain,
                operator_type=self.cdn_config.get("operator_type", 1),
                channel=self.cdn_config.get("channel"),
                from_app=self.cdn_config.get("from_app"),
                max_size=self.cdn_config.get("max_size"),  # 默认10MB
            )

            return result.get("attachment_url")
        finally:
            # 6. 清理临时文件
            if temp_file and temp_file.exists():
                temp_file.unlink()
                logger.debug(f"临时文件已删除: {temp_file}")

    @classmethod
    def supports(cls, file_path: Union[str, Path]) -> bool:
        """
        检查是否为飞书URL（类方法）

        Args:
            file_path: 文件路径或URL

        Returns:
            是否支持
        """
        url = str(file_path)
        return (
            url.startswith("https://")
            and ("/wiki/" in url or "/docx/" in url)
            and "feishu.cn" in url
        )

    def supported_types(self) -> List[str]:
        """
        返回支持的文件类型

        Returns:
            文件扩展名列表
        """
        return list(self.SUPPORTED_TYPES.keys())
