"""AIGC加载器测试"""

import pytest

from yz_doc import YZDoc
from yz_doc.core.document import Document


class TestAIGCLoader:
    """AIGC加载器测试"""

    def test_load_image_url(self):
        """测试加载图片URL"""
        # 创建YZDoc处理器
        doc_processor = YZDoc()

        # 测试图片URL
        image_url = "https://img01.yzcdn.cn/upload_files/2025/12/31/Fg43yRJaTwLoVzbts4zFc8gNn0Hh.jpeg"

        # 加载文档
        doc = doc_processor.load(image_url)

        # 验证加载结果
        assert isinstance(doc, Document)
        assert doc.doc_type == "image"
        assert doc.source == image_url
        assert len(doc.content) > 0
        assert doc.doc_id is not None

        # 验证元数据
        assert "loader" in doc.metadata
        assert doc.metadata["loader"] == "aigc"
        assert "url" in doc.metadata
        assert doc.metadata["url"] == image_url
        assert "source_type" in doc.metadata
        assert doc.metadata["source_type"] == "remote"
        assert "backend" in doc.metadata

        print(f"\n✓ AIGC加载器测试通过")
        print(f"  - URL: {image_url}")
        print(f"  - 文档类型: {doc.doc_type}")
        print(f"  - 内容长度: {len(doc.content)} 字符")
        print(f"  - 后端: {doc.metadata.get('backend', 'unknown')}")
        print(f"  - 内容预览: {doc.content[:200]}...")


if __name__ == "__main__":
    # 允许直接运行测试
    pytest.main([__file__, "-v", "-s"])
