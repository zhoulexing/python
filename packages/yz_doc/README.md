# YZ-Doc

有赞文档处理 SDK - 支持多格式文档加载与智能切分

## 安装

```bash
pip install yz-doc
```

## 快速开始

```python
from yz_doc import YZDoc

# 创建文档处理器
doc_processor = YZDoc()

# 加载文档
doc = doc_processor.load("path/to/file.md")

# 切分文档
chunks = doc_processor.split(doc, chunk_size=500, chunk_overlap=100)

# 查看结果
for chunk in chunks:
    print(f"Chunk {chunk.index}: {chunk.content[:100]}...")
```

## 支持的文档格式

| 格式     | 扩展名                                                   | 加载器    | 说明           |
| -------- | -------------------------------------------------------- | --------- | -------------- |
| 文本     | `.txt`                                                   | LangChain | 支持本地和URL  |
| Markdown | `.md`, `.markdown`                                       | LangChain | 支持本地和URL  |
| Excel    | `.xlsx`, `.xls`                                          | LangChain | 仅支持本地文件 |
| PDF      | `.pdf`                                                   | AIGC      | 仅支持URL      |
| Word     | `.doc`, `.docx`                                          | AIGC      | 仅支持URL      |
| 图片     | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`, `.jp2` | AIGC      | 仅支持URL      |
| 飞书文档 | 飞书URL                                                  | Feishu    | 需配置飞书应用 |

## 使用示例

### 1. 加载本地文件

```python
from yz_doc import YZDoc

doc_processor = YZDoc()

# Markdown 文件
doc = doc_processor.load("README.md")
print(f"内容: {doc.content[:200]}...")

# Excel 文件
doc = doc_processor.load("data.xlsx")
```

### 2. 加载网络文件

```python
doc = doc_processor.load("https://img.yzcdn.cn/upload_files/2025/12/31/image.jpg")
```

### 3. 加载飞书文档

```python
# 基础配置（不处理图片）
doc_processor = YZDoc(
    loader_config={
        "feishu": {
            "app_id": "your_app_id",
            "app_secret": "your_app_secret",
        }
    }
)

# 加载飞书文档
doc = doc_processor.load("https://youzan.feishu.cn/wiki/xxx")
```

**处理飞书文档中的图片**：

如果需要下载并上传飞书文档中的图片到 CDN，需要额外配置：

```python
doc_processor = YZDoc(
    loader_config={
        "feishu": {
            "app_id": "your_app_id",
            "app_secret": "your_app_secret",
            "download_images": True,  # 启用图片下载
            "cdn": {
                "operator_id": 123456,  # 操作员ID
                "channel": "your_channel",  # 渠道
                "operator_type": 1,  # 操作员类型（可选，默认1）
                "from_app": "your_app",  # 来源应用（可选）
                "max_size": 10485760,  # 最大文件大小（可选，默认10MB）
            }
        }
    }
)

# 加载飞书文档，图片会自动下载并上传到七牛云
doc = doc_processor.load("https://youzan.feishu.cn/wiki/xxx")
```

### 4. 切分文档

```python
# 文本切分
chunks = doc_processor.split(
    doc,
    splitter_type="text",
    chunk_size=500,
    chunk_overlap=100
)

# Markdown 按标题切分
chunks = doc_processor.split(
    doc,
    splitter_type="markdown",
    chunk_size=500,
    chunk_overlap=100
)

# 查看切片信息
for chunk in chunks:
    print(f"Chunk {chunk.index}: {len(chunk.content)} 字符")
```

### 5. 一站式处理

```python
# 直接加载并切分
chunks = doc_processor.process(
    "file.md",
    splitter_type="text",
    chunk_size=500,
    chunk_overlap=100
)

print(f"共切分为 {len(chunks)} 个片段")
```

## 文档对象

```python
doc.doc_id        # 文档唯一 ID
doc.content       # 文档内容
doc.doc_type      # 文档类型
doc.source        # 来源路径或 URL
doc.metadata      # 元数据字典
doc.created_at    # 创建时间
```

## 切片对象

```python
chunk.chunk_id      # 切片唯一 ID
chunk.content       # 切片内容
chunk.doc_id        # 所属文档 ID
chunk.index         # 在文档中的索引
chunk.metadata      # 元数据字典
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_langchain.py -v -s
pytest tests/test_aigc.py -v -s
pytest tests/test_feishu.py -v -s
```

---

**YZ-Doc - 让文档处理更简单** 🚀
