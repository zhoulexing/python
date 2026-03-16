"""飞书客户端：API 交互 + 文档块→Markdown 转换"""

import logging
from typing import List, Set, Optional, Tuple

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
from lark_oapi.api.docx.v1 import GetDocumentRequest, ListDocumentBlockRequest
from lark_oapi.api.drive.v1 import DownloadMediaRequest

from ..models import YzDocErrorCode, YzDocException

logger = logging.getLogger(__name__)


# ──────────────────────────── 块类型常量 ────────────────────────────


class DocxBlockType:
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
    DIVIDER = 22
    IMAGE = 27
    TABLE = 31
    TABLE_CELL = 32
    QUOTE_CONTAINER = 34


# ──────────────────────────── Markdown 转换 ────────────────────────────


class FeishuDocument:
    """飞书文档对象，负责文档块→Markdown 转换"""

    def __init__(self, document, blocks: List):
        self.document = document
        self.blocks = blocks
        self.block_map = {b.block_id: b for b in blocks}
        self.img_tokens: Set[str] = set()
        self.markdown_content: Optional[str] = None

    def to_markdown(self) -> Tuple[str, Set[str]]:
        if self.markdown_content is None:
            entry_block = self.block_map[self.document.document_id]
            self.markdown_content = self._parse_block(entry_block, 0)
        return self.markdown_content, self.img_tokens

    def _parse_block(self, block, indent_level: int) -> str:
        parts = []
        if indent_level > 0:
            parts.append("\t" * indent_level)

        bt = block.block_type
        if bt == DocxBlockType.PAGE:
            parts.append(self._parse_block_page(block))
        elif bt == DocxBlockType.TEXT:
            parts.append(self._parse_block_text(block.text))
        elif DocxBlockType.HEADING_1 <= bt <= DocxBlockType.HEADING_9:
            parts.append(self._parse_block_heading(block, bt - DocxBlockType.HEADING_1 + 1))
        elif bt == DocxBlockType.BULLET_LIST:
            parts.append(self._parse_block_bullet(block, indent_level))
        elif bt == DocxBlockType.ORDERED_LIST:
            parts.append(self._parse_block_ordered(block, indent_level))
        elif bt == DocxBlockType.CODE_BLOCK:
            parts.append(f"```\n{self._parse_block_text(block.code)}\n```\n")
        elif bt == DocxBlockType.QUOTE:
            parts.append(f"> {self._parse_block_text(block.quote)}")
        elif bt == DocxBlockType.TODO:
            checkbox = "[x]" if block.todo.style.done else "[ ]"
            parts.append(f"- {checkbox} {self._parse_block_text(block.todo)}")
        elif bt == DocxBlockType.DIVIDER:
            parts.append("---\n")
        elif bt == DocxBlockType.IMAGE:
            parts.append(self._parse_block_image(block.image))
        elif bt == DocxBlockType.TABLE:
            parts.append(self._parse_block_table(block.table))
        elif bt == DocxBlockType.TABLE_CELL:
            parts.append(self._parse_block_table_cell(block))
        elif bt == DocxBlockType.QUOTE_CONTAINER:
            parts.append(self._parse_block_quote_container(block))
        elif bt == DocxBlockType.GRID:
            parts.append(self._parse_block_grid(block, indent_level))

        return "".join(parts)

    # ── 各类块解析 ──

    def _parse_block_page(self, block) -> str:
        texts = ["# ", self._parse_block_text(block.page), "\n"]
        for child_id in block.children:
            texts.append(self._parse_block(self.block_map[child_id], 0))
            texts.append("\n")
        return "".join(texts)

    def _parse_block_text(self, text) -> str:
        buf = []
        num_elem = len(text.elements)
        for e in text.elements:
            buf.append(self._parse_text_element(e, num_elem > 1))
        buf.append("\n")
        return "".join(buf)

    def _parse_text_element(self, element, inline: bool) -> str:
        buf = []
        if element.text_run:
            buf.append(self._parse_text_run(element.text_run))
        if element.mention_user:
            buf.append(element.mention_user.user_id)
        if element.mention_doc:
            buf.append(f"[{element.mention_doc.title}]({element.mention_doc.url})")
        if element.equation:
            sym = "$" if inline else "$$"
            buf.append(sym + element.equation.content.rstrip("\n") + sym)
        return "".join(buf)

    def _parse_text_run(self, text_run) -> str:
        buf = []
        post = ""
        style = text_run.text_element_style
        if style:
            if style.bold:
                buf.append("**"); post = "**"
            elif style.italic:
                buf.append("_"); post = "_"
            elif style.strikethrough:
                buf.append("~~"); post = "~~"
            elif style.underline:
                buf.append("<u>"); post = "</u>"
            elif style.inline_code:
                buf.append("`"); post = "`"
            elif style.link:
                buf.append("["); post = f"]({style.link.url})"
        buf.append(text_run.content)
        buf.append(post)
        return "".join(buf)

    def _parse_block_heading(self, block, level: int) -> str:
        buf = ["#" * level, " "]
        buf.append(self._parse_block_text(getattr(block, f"heading{level}")))
        if block.children:
            for cid in block.children:
                buf.append(self._parse_block(self.block_map[cid], 0))
        return "".join(buf)

    def _parse_block_bullet(self, block, indent_level: int) -> str:
        buf = ["- ", self._parse_block_text(block.bullet)]
        if block.children:
            for cid in block.children:
                buf.append(self._parse_block(self.block_map[cid], indent_level + 1))
        return "".join(buf)

    def _parse_block_ordered(self, block, indent_level: int) -> str:
        parent = self.block_map[block.parent_id]
        order = 1
        for idx, child in enumerate(parent.children):
            if child == block.block_id:
                for i in range(idx - 1, -1, -1):
                    if self.block_map[parent.children[i]].block_type == DocxBlockType.ORDERED_LIST:
                        order += 1
                    else:
                        break
                break
        buf = [f"{order}. ", self._parse_block_text(block.ordered)]
        if block.children:
            for cid in block.children:
                buf.append(self._parse_block(self.block_map[cid], indent_level + 1))
        return "".join(buf)

    def _parse_block_image(self, image) -> str:
        self.img_tokens.add(image.token)
        return f"![]({image.token})\n"

    def _parse_block_table(self, table) -> str:
        rows = []
        for i, block_id in enumerate(table.cells):
            cell = self._parse_block(self.block_map[block_id], 0).replace("\n", "")
            row_idx = i // table.property.column_size
            if len(rows) < row_idx + 1:
                rows.append([])
            rows[row_idx].append(cell)
        return self._render_markdown_table(rows) + "\n"

    def _parse_block_table_cell(self, block) -> str:
        return "".join(
            self._parse_block(self.block_map[cid], 0) for cid in block.children
        )

    def _parse_block_quote_container(self, block) -> str:
        buf = []
        if block.children:
            for cid in block.children:
                buf.append("> ")
                buf.append(self._parse_block(self.block_map[cid], 0))
        return "".join(buf)

    def _parse_block_grid(self, block, indent_level: int) -> str:
        buf = []
        if block.children:
            for cid in block.children:
                col = self.block_map[cid]
                for ccid in col.children:
                    buf.append(self._parse_block(self.block_map[ccid], indent_level))
        return "".join(buf)

    @staticmethod
    def _render_markdown_table(rows: List[List[str]]) -> str:
        buf = []
        header_parsed = False
        for row in rows:
            buf.append("| " + " | ".join(row) + " |\n")
            if not header_parsed:
                buf.append("| " + " --- | " * len(row) + "\n")
                header_parsed = True
        return "".join(buf)


# ──────────────────────────── API 客户端 ────────────────────────────


class FeishuClient:
    """飞书 API 客户端"""

    def __init__(self, app_id: str, app_secret: str, proxy_domain: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.proxy_domain = proxy_domain

        self.client = (
            lark.Client.builder()
            .app_id(self.app_id)
            .app_secret(self.app_secret)
            .enable_set_token(True)
            .log_level(lark.LogLevel.ERROR)
            .domain(self.proxy_domain)
            .build()
        )

    def get_config(self):
        config = Config()
        config.app_id = self.app_id
        config.app_secret = self.app_secret
        config.domain = self.proxy_domain
        return config

    def get_request_headers(self, need_access_token: bool = False):
        headers = RequestOption.builder().headers({
            "scheme": "https",
            "Host": "open.feishu.cn",
            "yzc-connect-timeout": "4000",
            "yzc-send-timeout": "200000",
            "yzc-read-timeout": "200000",
        }).build()

        if need_access_token:
            req = (
                CreateSelfTenantTokenRequest.builder()
                .request_body(
                    CreateTokenRequestBody.builder()
                    .app_id(self.app_id)
                    .app_secret(self.app_secret)
                    .build()
                )
                .build()
            )
            raw: RawResponse = Transport.execute(self.get_config(), req, headers)
            resp = JSON.unmarshal(str(raw.content, UTF_8), AccessTokenResponse)

            if not resp.success():
                raise YzDocException(
                    YzDocErrorCode.FAILED_TO_OBTAIN_ACCESS_TOKEN,
                    f"飞书获取访问令牌失败: {resp.code}, {resp.msg}",
                )
            headers.tenant_access_token = resp.tenant_access_token

        return headers

    def get_wiki_obj_token(self, wiki_token: str) -> str:
        resp = self.client.wiki.v2.space.get_node(
            GetNodeSpaceRequest.builder().token(wiki_token).build(),
            self.get_request_headers(True),
        )
        if resp.code != 0:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_GET_WIKI_OBJ_TOKEN,
                f"飞书获取Wiki文档对象token失败: {resp.msg}",
            )
        return resp.data.node.obj_token

    def get_document(self, obj_token: str):
        resp = self.client.docx.v1.document.get(
            GetDocumentRequest.builder().document_id(obj_token).build(),
            self.get_request_headers(True),
        )
        if resp.raw.status_code == 403:
            raise YzDocException(
                YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                f"请先完成该文档的授权: {resp.msg}",
            )
        if resp.code != 0:
            raise YzDocException(
                YzDocErrorCode.FAILED_TO_GET_DOCUMENT, f"飞书获取文档失败: {resp.msg}"
            )
        return resp.data.document

    def get_blocks(self, obj_token: str) -> List:
        blocks = []
        page_token = None
        while True:
            builder = ListDocumentBlockRequest.builder().document_id(obj_token)
            if page_token:
                builder = builder.page_token(page_token)
            resp = self.client.docx.v1.document_block.list(
                builder.build(), self.get_request_headers(True)
            )
            if resp.raw.status_code == 403:
                raise YzDocException(
                    YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                    f"请先完成该文档的授权: {resp.msg}",
                )
            if resp.code != 0:
                raise YzDocException(
                    YzDocErrorCode.FAILED_TO_GET_BLOCKS, f"飞书获取文档块失败: {resp.msg}"
                )
            blocks.extend(resp.data.items)
            if not resp.data.has_more:
                break
            page_token = resp.data.page_token
        return blocks

    def download_image(self, file_token: str) -> bytes:
        resp = self.client.drive.v1.media.download(
            DownloadMediaRequest.builder().file_token(file_token).build(),
            self.get_request_headers(True),
        )
        if resp.file is None and resp.raw.status_code == 403:
            raise YzDocException(
                YzDocErrorCode.DOCUMENT_NOT_AUTHORIZED,
                f"请先完成该文档的授权: {resp.msg}",
            )
        return resp.file.read()
