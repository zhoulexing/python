"""
异常定义与错误码映射
"""
from typing import Optional
from enum import Enum

class YzDocErrorCode(Enum):
    """YZ-Doc 错误码定义

    格式: (错误码, 错误信息)
    """
    UNSUPPORTED_FILE_TYPE_ERROR = (20000001, "不支持的文件类型")
    REMOTE_EXCEL_FILES_NOT_SUPPORTED = (20000002, "远程Excel文件不支持")
    FAILED_TO_LOAD_MARKDOWN_FILE = (20000003, "加载Markdown文件失败")
    FAILED_TO_LOAD_TEXT_FILE = (20000004, "加载文本文件失败")
    FAILED_TO_LOAD_WEB_PAGE = (20000005, "加载网页失败")
    FAILED_TO_LOAD_EXCEL_FILE = (20000006, "加载Excel文件失败")
    INVALID_SPLITTER_CLASS = (20000008, "无效的切分器类")
    SPLITTER_NOT_FOUND = (20000009, "切分器未找到")
    DOCUMENT_CONTENT_EMPTY = (20000010, "文档内容为空")
    DOCUMENT_DOC_ID_MISSING = (20000011, "文档ID缺失")
    MARKDOWN_HEADER_TEXT_SPLITTER_NOT_AVAILABLE = (20000012, "MarkdownHeaderTextSplitter未找到")
    FAILED_TO_SPLIT_DOCUMENT = (20000013, "切分文档失败")
    RECURSIVE_CHARACTER_TEXT_SPLITTER_NOT_AVAILABLE = (20000014, "RecursiveCharacterTextSplitter未找到")
    FAILED_TO_OBTAIN_ACCESS_TOKEN = (20000015, "飞书获取访问令牌失败")
    FAILED_TO_GET_WIKI_OBJ_TOKEN = (20000016, "飞书获取Wiki文档对象token失败")
    DOCUMENT_NOT_AUTHORIZED = (20000017, "文档未授权")
    FAILED_TO_GET_DOCUMENT = (20000018, "飞书获取文档失败")
    FAILED_TO_GET_BLOCKS = (20000019, "飞书获取文档块失败")
    FILE_NOT_FOUND = (20000020, "文件不存在")
    FILE_SIZE_EXCEEDS_MAXIMUM_ALLOWED_SIZE = (20000021, "文件大小超过最大允许大小")
    NOT_IMPLEMENTED = (20000022, "未实现")
    FAILED_TO_GET_UPLOAD_TOKEN = (20000023, "无法从响应中提取token")
    FEISHU_CONFIG_NOT_SET = (20000024, "飞书相关参数未配置")
    CDN_CONFIG_NOT_SET = (20000025, "CDN配置未设置")
    UNSUPPORTED_CDN_PROVIDER = (20000026, "不支持的CDN提供商")
    FAILED_TO_LOAD_FEISHU_DOCUMENT = (20000027, "加载飞书文档失败")
    UNSUPPORTED_FEISHU_URL_FORMAT = (20000028, "不支持的飞书URL格式")
    CDN_CONFIG_MISSING_OPERATOR_ID = (20000029, "CDN配置缺少operator_id参数")
    CDN_CONFIG_MISSING_PROXY_DOMAIN = (20000030, "CDN配置缺少proxy_domain参数")
    UPLOAD_RESULT_MISSING_KEY = (20000031, "上传结果中缺少key字段")
    FAILED_TO_UPLOAD_IMAGE_TO_QINIU = (20000032, "上传图片到七牛云失败")
    FAILED_TO_CALL_AIGC_API = (20000033, "调用AIGC解析API失败")
    AIGC_API_PARSE_ERROR = (20000034, "AIGC API返回错误")
    AIGC_API_RESPONSE_INVALID = (20000035, "AIGC API响应格式无效")
    AIGC_API_CONFIG_NOT_SET = (20000036, "AIGC API配置未设置")
    LOCAL_FILES_NOT_SUPPORTED_BY_AIGC = (20000037, "AIGC加载器不支持本地文件")
    FAILED_TO_LOAD_DOCUMENT = (20000038, "加载文档失败")

    @property
    def code(self) -> int:
        return self.value[0]
    
    @property
    def message(self) -> str:
        return self.value[1]

class YzDocException(Exception):
    """YZ-Doc 调用异常基类"""

    def __init__(
        self,
        error_code: YzDocErrorCode,
        message: Optional[str] = None,
    ) -> None:
        """
        初始化 YZ-Doc 异常

        Args:
            error_code: 错误码元组 (code, default_message)
            message: 自定义错误信息，如果不提供则使用默认信息
        """
        self.code = error_code.code
        self.message = message or error_code.message
        super().__init__(self.message)
