"""飞书文档处理工具类"""
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest
from lark_oapi.core.model import RequestOption
from lark_oapi.core.http import Transport
from lark_oapi.core.token.create_self_tenant_token_request import CreateSelfTenantTokenRequest
from lark_oapi.core.token.create_token_request_body import CreateTokenRequestBody
from lark_oapi.core.model import Config, RawResponse
from lark_oapi.core import JSON
from lark_oapi.core.const import UTF_8
from lark_oapi.core.token.access_token_response import AccessTokenResponse
from lark_oapi.api.docx.v1 import GetDocumentRequest
from lark_oapi.api.docx.v1 import ListDocumentBlockRequest
from lark_oapi.api.drive.v1 import DownloadMediaRequest
from yz_doc.core.exceptions import YzDocErrorCode, YzDocException

from typing import List, Set, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DocxBlockType:
    """飞书文档块类型常量"""
    PAGE = 1
    TEXT = 2
    HEADING_1 = 3
    HEADING_2 = 4
    HEADING_3 = 5
    HEADING_4 = 6
    HEADING_5 = 7
    HEADING_6 = 8
    HEADING_7 = 9
    HEADING_8 = 10
    HEADING_9 = 11
    BULLET_LIST = 12
    ORDERED_LIST = 13
    CODE_BLOCK = 14
    QUOTE = 15
    TODO = 17
    GRID = 18
    HIGHLIGHT = 19
    CHAT_CARD = 20
    FLOW_CHART = 21
    DIVIDER = 22
    FILE = 23
    COLUMN = 24
    COLUMN_ITEM = 25
    EMBEDDED_PAGE = 26
    IMAGE = 27
    OPEN_PLATFORM_WIDGET = 28
    NOTE = 29
    SPREADSHEET = 30
    TABLE = 31
    TABLE_CELL = 32
    VIEW = 33
    QUOTE_CONTAINER = 34
    TASK = 35
    OKR = 36
    OKR_OBJECTIVE = 37
    OKR_KEY_RESULT = 38
    OKR_PROGRESS = 39
    DOC_WIDGET = 40
    JIRA_ISSUE = 41
    WIKI_SUBDIR = 42
    DRAWING_BOARD = 43
    UNSUPPORTED = 999


class FeishuDocument:
    """
    飞书文档对象,负责文档到Markdown的转换

    复用现有的LarkDocument逻辑,支持所有飞书文档块类型
    """

    def __init__(self, document, blocks: List):
        """
        初始化飞书文档

        Args:
            document: 飞书文档对象(lark_oapi Document)
            blocks: 文档块列表(lark_oapi Block列表)
        """
        self.document = document
        self.blocks = blocks
        self.block_map = {b.block_id: b for b in blocks}
        self.img_tokens: Set[str] = set()
        self.markdown_content: Optional[str] = None

    def to_markdown(self) -> Tuple[str, Set[str]]:
        """
        转换为Markdown格式

        Returns:
            (markdown_content, img_tokens): Markdown内容和图片token集合
        """
        if self.markdown_content is None:
            entry_block = self.block_map[self.document.document_id]
            self.markdown_content = self._parse_block(entry_block, 0)
        return self.markdown_content, self.img_tokens

    def _parse_block(self, block, indent_level: int) -> str:
        """
        解析单个文档块

        Args:
            block: 飞书文档块对象
            indent_level: 缩进级别

        Returns:
            解析后的Markdown文本
        """
        block_contents = []

        # 添加缩进
        if indent_level > 0:
            block_contents.append('\t' * indent_level)

        # 根据块类型解析
        if block.block_type == DocxBlockType.PAGE:
            block_contents.append(self._parse_block_page(block))
        elif block.block_type == DocxBlockType.TEXT:
            block_contents.append(self._parse_block_text(block.text))
        elif DocxBlockType.HEADING_1 <= block.block_type <= DocxBlockType.HEADING_9:
            heading_level = block.block_type - DocxBlockType.HEADING_1 + 1
            block_contents.append(
                self._parse_block_heading(block, heading_level))
        elif block.block_type == DocxBlockType.BULLET_LIST:
            block_contents.append(
                self._parse_block_bullet(block, indent_level))
        elif block.block_type == DocxBlockType.ORDERED_LIST:
            block_contents.append(
                self._parse_block_ordered(block, indent_level))
        elif block.block_type == DocxBlockType.CODE_BLOCK:
            block_contents.append(self._parse_block_code(block))
        elif block.block_type == DocxBlockType.QUOTE:
            block_contents.append(self._parse_block_quote(block))
        elif block.block_type == DocxBlockType.TODO:
            block_contents.append(self._parse_block_todo(block))
        elif block.block_type == DocxBlockType.DIVIDER:
            block_contents.append("---\n")
        elif block.block_type == DocxBlockType.IMAGE:
            block_contents.append(self._parse_block_image(block.image))
        elif block.block_type == DocxBlockType.TABLE:
            block_contents.append(self._parse_block_table(block.table))
        elif block.block_type == DocxBlockType.TABLE_CELL:
            block_contents.append(self._parse_block_table_cell(block))
        elif block.block_type == DocxBlockType.QUOTE_CONTAINER:
            block_contents.append(self._parse_block_quote_container(block))
        elif block.block_type == DocxBlockType.GRID:
            block_contents.append(self._parse_block_grid(block, indent_level))

        return ''.join(block_contents)

    def _parse_block_page(self, block) -> str:
        """解析页面块"""
        texts = ["# ", self._parse_block_text(block.page), "\n"]
        for child_id in block.children:
            child_block = self.block_map[child_id]
            texts.append(self._parse_block(child_block, 0))
            texts.append("\n")
        return ''.join(texts)

    def _parse_block_text(self, text) -> str:
        """解析文本块"""
        buf = []
        num_elem = len(text.elements)
        for e in text.elements:
            inline = num_elem > 1
            buf.append(self._parse_text_element(e, inline))
        buf.append("\n")
        return ''.join(buf)

    def _parse_text_element(self, element, inline: bool) -> str:
        """解析文本元素"""
        buf = []
        if element.text_run:
            buf.append(self._parse_text_run(element.text_run))
        if element.mention_user:
            buf.append(element.mention_user.user_id)
        if element.mention_doc:
            buf.append(
                f"[{element.mention_doc.title}]({element.mention_doc.url})")
        if element.equation:
            symbol = "$$" if not inline else "$"
            buf.append(symbol + element.equation.content.rstrip("\n") + symbol)
        return ''.join(buf)

    def _parse_text_run(self, text_run) -> str:
        """解析文本运行(处理样式)"""
        buf = []
        post_write = ""
        style = text_run.text_element_style

        if style:
            if style.bold:
                buf.append("**")
                post_write = "**"
            elif style.italic:
                buf.append("_")
                post_write = "_"
            elif style.strikethrough:
                buf.append("~~")
                post_write = "~~"
            elif style.underline:
                buf.append("<u>")
                post_write = "</u>"
            elif style.inline_code:
                buf.append("`")
                post_write = "`"
            elif style.link:
                buf.append("[")
                post_write = f"]({style.link.url})"

        buf.append(text_run.content)
        buf.append(post_write)
        return ''.join(buf)

    def _parse_block_heading(self, block, level: int) -> str:
        """解析标题块"""
        buf = ["#" * level, " "]
        heading_text = getattr(block, f"heading{level}")
        buf.append(self._parse_block_text(heading_text))
        if block.children:
            for child_id in block.children:
                child_block = self.block_map[child_id]
                buf.append(self._parse_block(child_block, 0))
        return ''.join(buf)

    def _parse_block_bullet(self, block, indent_level: int) -> str:
        """解析无序列表块"""
        buf = ["- ", self._parse_block_text(block.bullet)]
        if block.children:
            for child_id in block.children:
                child_block = self.block_map[child_id]
                buf.append(self._parse_block(child_block, indent_level + 1))
        return ''.join(buf)

    def _parse_block_ordered(self, block, indent_level: int) -> str:
        """解析有序列表块"""
        buf = []
        parent = self.block_map[block.parent_id]
        order = 1

        # 计算序号
        for idx, child in enumerate(parent.children):
            if child == block.block_id:
                for i in range(idx - 1, -1, -1):
                    if self.block_map[parent.children[i]].block_type == DocxBlockType.ORDERED_LIST:
                        order += 1
                    else:
                        break
                break

        buf.append(f"{order}. ")
        buf.append(self._parse_block_text(block.ordered))
        if block.children:
            for child_id in block.children:
                child_block = self.block_map[child_id]
                buf.append(self._parse_block(child_block, indent_level + 1))
        return ''.join(buf)

    def _parse_block_code(self, block) -> str:
        """解析代码块"""
        return f"```\n{self._parse_block_text(block.code)}\n```\n"

    def _parse_block_quote(self, block) -> str:
        """解析引用块"""
        return f"> {self._parse_block_text(block.quote)}"

    def _parse_block_todo(self, block) -> str:
        """解析待办块"""
        checkbox = "[x]" if block.todo.style.done else "[ ]"
        return f"- {checkbox} {self._parse_block_text(block.todo)}"

    def _parse_block_image(self, image) -> str:
        """解析图片块"""
        self.img_tokens.add(image.token)
        return f"![]({image.token})\n"

    def _parse_block_table(self, table) -> str:
        """解析表格块"""
        rows = []
        for i, block_id in enumerate(table.cells):
            cell_block = self.block_map[block_id]
            cell_content = self._parse_block(cell_block, 0).replace("\n", "")
            row_index = i // table.property.column_size
            if len(rows) < row_index + 1:
                rows.append([])
            rows[row_index].append(cell_content)
        return self._render_markdown_table(rows) + "\n"

    def _parse_block_table_cell(self, block) -> str:
        """解析表格单元格块"""
        buf = []
        for child_id in block.children:
            child_block = self.block_map[child_id]
            content = self._parse_block(child_block, 0)
            buf.append(content)
        return ''.join(buf)

    def _parse_block_quote_container(self, block) -> str:
        """解析引用容器块"""
        buf = []
        if block.children:
            for child_id in block.children:
                child_block = self.block_map[child_id]
                buf.append("> ")
                buf.append(self._parse_block(child_block, 0))
        return ''.join(buf)

    def _parse_block_grid(self, block, indent_level: int) -> str:
        """解析网格布局块"""
        buf = []
        if block.children:
            for child_id in block.children:
                column_block = self.block_map[child_id]
                for column_child_id in column_block.children:
                    child_block = self.block_map[column_child_id]
                    buf.append(self._parse_block(child_block, indent_level))
        return ''.join(buf)

    @staticmethod
    def _render_markdown_table(rows: List[List[str]]) -> str:
        """渲染Markdown表格"""
        buf = []
        header_row_parsed = False
        for row in rows:
            buf.append('| ' + ' | '.join(row) + ' |')
            buf.append('\n')
            if not header_row_parsed:
                buf.append('| ' + ' --- | ' * len(row) + '\n')
                header_row_parsed = True
        return ''.join(buf)


class FeishuClient:
    """飞书客户端工具类"""

    def __init__(self, app_id: str, app_secret: str, proxy_domain: str):
        """
        初始化飞书客户端

        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            proxy_domain: 飞书代理域名
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy_domain = proxy_domain

        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.ERROR) \
            .domain(self.proxy_domain) \
            .build()

    def get_config(self):
        config = Config()
        config.app_id = self.app_id
        config.app_secret = self.app_secret
        config.domain = self.proxy_domain
        return config

    def get_request_headers(self, need_access_token: bool = False):
        headers = RequestOption.builder().headers({
            'scheme': 'https',
            'Host': 'open.feishu.cn',
            'yzc-connect-timeout': '4000',
            'yzc-send-timeout': '200000',
            'yzc-read-timeout': '200000',
        }).build()

        if need_access_token:
            req: CreateSelfTenantTokenRequest = CreateSelfTenantTokenRequest.builder() \
                .request_body(CreateTokenRequestBody.builder()
                              .app_id(self.app_id)
                              .app_secret(self.app_secret)
                              .build()) \
                .build()
            raw: RawResponse = Transport.execute(
                self.get_config(), req, headers)
            resp = JSON.unmarshal(str(raw.content, UTF_8), AccessTokenResponse)

            if not resp.success():
                raise YzDocException(YzDocErrorCode.FAILED_TO_OBTAIN_ACCESS_TOKEN,
                                     f"飞书获取访问令牌失败: {resp.code}, {resp.msg}")

            headers.tenant_access_token = resp.tenant_access_token

        return headers

    def get_wiki_obj_token(self, wiki_token: str) -> str:
        """
        获取Wiki文档的obj_token

        Args:
            wiki_token: Wiki文档token

        Returns:
            文档对象token

        Raises:
            Exception: 获取失败时抛出
        """
        resp = self.client.wiki.v2.space.get_node(
            GetNodeSpaceRequest.builder().token(wiki_token).build(),
            self.get_request_headers(True)
        )

        if resp.code != 0:
            raise YzDocException(YzDocErrorCode.FAILED_TO_GET_WIKI_OBJ_TOKEN,
                                 f"飞书获取Wiki文档对象token失败: {resp.msg}")

        return resp.data.node.obj_token

    def get_document(self, obj_token: str):
        """
        获取文档基础信息

        Args:
            obj_token: 文档对象token

        Returns:
            Document对象

        Raises:
            PermissionError: 文档未授权时抛出
            Exception: 获取失败时抛出
        """
        resp = self.client.docx.v1.document.get(
            GetDocumentRequest.builder().document_id(obj_token).build(),
            self.get_request_headers(True)
        )

        if resp.raw.status_code == 403:
            raise YzDocException(YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                                 f"请先完成该文档的授权: {resp.msg}")

        if resp.code != 0:
            raise YzDocException(YzDocErrorCode.FAILED_TO_GET_DOCUMENT,
                                 f"飞书获取文档失败: {resp.msg}")

        return resp.data.document

    def get_blocks(self, obj_token: str) -> List:
        """
        分页获取文档所有块

        Args:
            obj_token: 文档对象token

        Returns:
            Block列表

        Raises:
            PermissionError: 文档未授权时抛出
            Exception: 获取失败时抛出
        """
        blocks = []
        page_token = None

        while True:
            if page_token:
                req = ListDocumentBlockRequest.builder() \
                    .document_id(obj_token) \
                    .page_token(page_token) \
                    .build()
            else:
                req = ListDocumentBlockRequest.builder() \
                    .document_id(obj_token) \
                    .build()

            resp = self.client.docx.v1.document_block.list(
                req, self.get_request_headers(True))

            if resp.raw.status_code == 403:
                raise YzDocException(YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                                     f"请先完成该文档的授权: {resp.msg}")

            if resp.code != 0:
                raise YzDocException(YzDocErrorCode.FAILED_TO_GET_BLOCKS,
                                     f"飞书获取文档块失败: {resp.msg}")

            blocks.extend(resp.data.items)

            if not resp.data.has_more:
                break
            else:
                page_token = resp.data.page_token

        return blocks

    def download_image(self, file_token: str) -> bytes:
        """
        下载图片

        Args:
            file_token: 图片文件token

        Returns:
            图片二进制数据

        Raises:
            PermissionError: 文档未授权时抛出
        """
        resp = self.client.drive.v1.media.download(
            DownloadMediaRequest.builder().file_token(file_token).build(),
            self.get_request_headers(True)
        )

        if resp.file is None and resp.raw.status_code == 403:
            raise YzDocException(YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                                 f"请先完成该文档的授权: {resp.msg}")

        return resp.file.read()
