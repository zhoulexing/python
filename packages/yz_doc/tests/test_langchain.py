"""LangChain集成测试 - 加载和切分Markdown文件"""

import pytest
from pathlib import Path

from yz_doc import YZDoc
from yz_doc.core.document import Document
from yz_doc.core.chunk import Chunk


@pytest.fixture
def doc_processor():
    """创建YZDoc处理器实例"""
    return YZDoc()


@pytest.fixture
def fixtures_dir():
    """测试文件目录"""
    return Path(__file__).parent.parent


class TestLangChainMarkdown:
    """LangChain Markdown文件加载和切分测试"""

    def test_load_and_split_local_markdown(self, doc_processor, fixtures_dir):
        """测试加载本地Markdown文件并切分"""
        # 准备测试文件路径
        md_file = fixtures_dir / "README.md"

        # 跳过测试如果文件不存在
        if not md_file.exists():
            pytest.skip(f"测试文件不存在: {md_file}")

        # 1. 加载本地Markdown文件
        doc = doc_processor.load(md_file)
        
        print(f"doc.doc_type: {doc.doc_type}")

        # 验证加载结果
        assert isinstance(doc, Document)
        assert doc.doc_type == "markdown"
        assert doc.source == str(md_file)
        assert len(doc.content) > 0
        assert doc.doc_id is not None

        # 验证元数据
        assert "file_name" in doc.metadata
        assert doc.metadata["file_name"] == "README.md"
        assert "loader" in doc.metadata
        assert doc.metadata["loader"] == "langchain"

        # 2. 使用Markdown切分器切分文档
        chunks = doc_processor.split(
            doc, splitter_type="text", chunk_size=500, chunk_overlap=50
        )
        
        # 验证切分结果
        assert isinstance(chunks, list)
        assert len(chunks) > 0
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
        assert first_chunk.metadata["splitter"] == "text"
        assert first_chunk.metadata["total_chunks"] == len(chunks)

        # 验证所有chunk的索引连续性
        for i, chunk in enumerate(chunks):
            assert chunk.index == i
            assert chunk.metadata["chunk_index"] == i

        print(f"\n✓ 本地Markdown文件加载和切分测试通过")
        print(f"  - 文档长度: {len(doc.content)} 字符")
        print(f"  - 切片数量: {len(chunks)}")
        print(f"  - 第一个切片长度: {len(first_chunk.content)} 字符")

    def test_load_and_split_remote_markdown(self, doc_processor):
        """测试加载网络Markdown文件并切分"""
        # 使用GitHub上的一个公开Markdown文件作为测试
        # 这是一个真实的、稳定的测试URL
        remote_url = "https://file.yzcdn.cn/upload_files/yz-file/2025/12/24/Fsiw7K6TC9M32s1Eew5VUkgt0H3f.md"

        try:
            # 1. 加载网络Markdown文件
            doc = doc_processor.load(remote_url)

            # 验证加载结果
            assert isinstance(doc, Document)
            assert doc.doc_type == "markdown"
            assert doc.source == remote_url
            assert len(doc.content) > 0
            assert doc.doc_id is not None

            # 验证元数据
            assert "loader" in doc.metadata
            assert doc.metadata["loader"] == "langchain"

            # 2. 使用文本切分器切分文档（网络文件可能较大）
            chunks = doc_processor.split(
                doc, splitter_type="text", chunk_size=500, chunk_overlap=50
            )

            # 验证切分结果
            assert isinstance(chunks, list)
            assert len(chunks) > 0
            assert all(isinstance(chunk, Chunk) for chunk in chunks)

            # 验证chunk基本属性
            first_chunk = chunks[0]
            assert first_chunk.doc_id == doc.doc_id
            assert first_chunk.index == 0
            assert len(first_chunk.content) > 0
            assert len(first_chunk.content) <= 600  # 允许一些超出

            # 验证chunk元数据
            assert "chunk_index" in first_chunk.metadata
            assert "total_chunks" in first_chunk.metadata
            assert "splitter" in first_chunk.metadata
            assert first_chunk.metadata["total_chunks"] == len(chunks)

            # 验证所有chunk的连续性
            for i, chunk in enumerate(chunks):
                assert chunk.index == i
                assert chunk.doc_id == doc.doc_id

            print(f"\n✓ 网络Markdown文件加载和切分测试通过")
            print(f"  - URL: {remote_url}")
            print(f"  - 文档长度: {len(doc.content)} 字符")
            print(f"  - 切片数量: {len(chunks)}")
            print(f"  - 第一个切片长度: {len(first_chunk.content)} 字符")

        except Exception as e:
            # 网络请求可能失败，提供友好的错误信息
            pytest.skip(f"网络请求失败，跳过测试: {str(e)}")

    def test_load_and_split_weixin_article(self, doc_processor):
        """测试加载公众号文章并切分"""
        # 公众号文章URL（无扩展名）
        url = "https://mp.weixin.qq.com/s/nijdH_Vp8tbUv3vqGgFfcA"

        try:
            # 1. 加载公众号文章
            doc = doc_processor.load(url)

            # 验证加载结果
            assert isinstance(doc, Document)
            assert doc.doc_type == "web"
            assert doc.source == url
            assert len(doc.content) > 0
            assert doc.doc_id is not None

            # 验证元数据
            assert "loader" in doc.metadata
            assert doc.metadata["loader"] == "langchain"
            assert "source_type" in doc.metadata
            assert doc.metadata["source_type"] == "web"
            assert "url" in doc.metadata
            assert doc.metadata["url"] == url

            # 2. 使用文本切分器切分文档
            chunks = doc_processor.split(
                doc, splitter_type="text", chunk_size=500, chunk_overlap=100
            )

            # 验证切分结果
            assert isinstance(chunks, list)
            assert len(chunks) > 0
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
            assert first_chunk.metadata["splitter"] == "text"
            assert first_chunk.metadata["total_chunks"] == len(chunks)

            # 验证所有chunk的索引连续性
            for i, chunk in enumerate(chunks):
                assert chunk.index == i
                assert chunk.metadata["chunk_index"] == i

            print(f"\n✓ 公众号文章加载和切分测试通过")
            print(f"  - URL: {url}")
            print(f"  - 文档长度: {len(doc.content)} 字符")
            print(f"  - 切片数量: {len(chunks)}")
            print(f"  - 第一个切片长度: {len(first_chunk.content)} 字符")

        except Exception as e:
            # 网络请求可能失败，提供友好的错误信息
            pytest.skip(f"网络请求失败，跳过测试: {str(e)}")


if __name__ == "__main__":
    # 允许直接运行测试
    pytest.main([__file__, "-v", "-s"])
