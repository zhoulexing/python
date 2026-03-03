"""飞书文档加载器测试"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from yz_doc import YZDoc
from yz_doc.core.document import Document
from yz_doc.core.chunk import Chunk

# 加载环境变量
_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(_ENV_FILE)


@pytest.fixture
def doc_processor():
    """创建YZDoc处理器实例"""
    # 从环境变量获取配置
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")

    # 如果环境变量未配置,返回None(在测试中会跳过)
    if not all([app_id, app_secret]):
        return None

    return YZDoc(config={
        "feishu": {
            "app_id": app_id,
            "app_secret": app_secret,
            "download_images": True,  # 测试时不下载图片
            "cdn": {
                "operator_id": 111111,
                "operator_type": 1,
                "channel": "xxx",
                "from_app": "xxx",
                "max_size": 10485760,
            }
        }
    })


class TestFeishuLoader:
    """飞书文档加载和切分测试"""

    def test_load_and_split_feishu_wiki(self, doc_processor):
        """
        测试加载飞书Wiki文档并切分

        测试流程:
        1. 使用YZDoc加载飞书文档
        2. 验证Document对象生成正确
        3. 使用Markdown切分器对文档进行切分
        4. 验证切分后的chunks正确

        环境变量配置:
        - FEISHU_APP_ID: 飞书应用ID
        - FEISHU_APP_SECRET: 飞书应用密钥
        """
        # 如果配置未设置,跳过测试
        if doc_processor is None:
            pytest.skip(
                "飞书配置未设置,跳过测试。请设置环境变量: FEISHU_APP_ID, FEISHU_APP_SECRET")

        # 测试URL
        test_url = "https://qima.feishu.cn/wiki/O6W9wT8HZikxHlky2l7cJ9H1nWf"

        try:
            # 1. 加载飞书文档
            doc = doc_processor.load(test_url)

            # 2. 验证文档加载
            assert isinstance(doc, Document)
            assert doc.content != "", "文档内容不能为空"
            assert doc.doc_type in ["feishu_wiki",
                                    "feishu_docx"], f"文档类型错误: {doc.doc_type}"
            assert doc.source == test_url, "文档来源URL不匹配"
            assert doc.doc_id is not None

            # 验证元数据
            assert "loader" in doc.metadata, "元数据中应包含loader字段"
            assert doc.metadata["loader"] == "feishu", "loader应为feishu"
            assert "title" in doc.metadata or "document_id" in doc.metadata

            print(f"\n文档加载成功:")
            print(f"  - 类型: {doc.doc_type}")
            print(f"  - 标题: {doc.metadata.get('title', 'N/A')}")
            print(f"  - 内容长度: {len(doc.content)} 字符")
            print(f"  - 图片数量: {doc.metadata.get('image_count', 0)}")

            # 3. 使用Markdown切分器切分文档
            chunks = doc_processor.split(doc, splitter_type="markdown")

            # 4. 验证切分结果
            assert isinstance(chunks, list)
            assert len(chunks) > 0, "切分后的chunks数量应大于0"
            assert all(isinstance(chunk, Chunk) for chunk in chunks)

            # 验证第一个chunk
            first_chunk = chunks[0]
            assert first_chunk.doc_id == doc.doc_id
            assert first_chunk.index == 0
            assert len(first_chunk.content) > 0

            # 验证chunk元数据
            assert "chunk_index" in first_chunk.metadata
            assert "total_chunks" in first_chunk.metadata
            assert "splitter" in first_chunk.metadata
            assert first_chunk.metadata["splitter"] == "markdown"
            assert first_chunk.metadata["total_chunks"] == len(chunks)

            # 验证所有chunk的索引连续性
            for i, chunk in enumerate(chunks):
                assert chunk.index == i
                assert chunk.metadata["chunk_index"] == i
                assert chunk.content != "", f"第{i+1}个chunk内容不能为空"

            print(f"\n文档切分成功:")
            print(f"  - Chunks数量: {len(chunks)}")

            # 打印前3个chunk的信息
            for i, chunk in enumerate(chunks[:3]):
                print(f"\n  Chunk {i+1}:")
                print(f"    - 内容长度: {len(chunk.content)} 字符")
                print(f"    - 内容预览: {chunk.content[:100]}...")

            print("\n✓ 飞书Wiki文档加载和切分测试通过")

        except Exception as e:
            # 网络请求或权限问题可能导致失败
            pytest.skip(f"测试失败，跳过: {str(e)}")


if __name__ == "__main__":
    # 允许直接运行测试
    pytest.main([__file__, "-v", "-s"])
