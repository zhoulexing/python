---
name: yz-doc
description: 多格式文档加载与智能切分工具。支持 txt、md、xlsx、pdf、docx、图片、飞书文档的加载，以及 text/markdown 两种切分策略。当需要读取文档内容、解析飞书文档、将长文本切分为 chunks 时使用此技能。触发词包括"加载文档"、"解析文档"、"读取飞书"、"文档切分"、"文本分块"等。
---

# YZ-Doc 文档处理

## 环境准备

首次使用需安装依赖：

```bash
bash agent/skills/yz-doc/scripts/setup.sh
```

## 命令列表

### 1. 加载文档 (doc_load.py)

```bash
# 本地文件（txt/md/xlsx 无需任何配置）
python agent/skills/yz-doc/scripts/doc_load.py README.md
python agent/skills/yz-doc/scripts/doc_load.py data.xlsx

# 远程文件（pdf/docx/图片，需为 URL）
python agent/skills/yz-doc/scripts/doc_load.py "https://example.com/file.pdf"

# 飞书文档（必须提供 app_id 和 app_secret）
python agent/skills/yz-doc/scripts/doc_load.py "https://xxx.feishu.cn/wiki/xxx" \
  --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET

# 输出到文件、指定格式
python agent/skills/yz-doc/scripts/doc_load.py file.md -o result.json --format json
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `source` | 是 | 文件路径或 URL |
| `--app-id` | 飞书必填 | 飞书应用 App ID（也可通过环境变量 `FEISHU_APP_ID` 设置） |
| `--app-secret` | 飞书必填 | 飞书应用 App Secret（也可通过环境变量 `FEISHU_APP_SECRET` 设置） |
| `--format` | 否 | 输出格式：`text`（默认）、`json`、`markdown` |
| `-o/--output` | 否 | 输出文件路径，不指定则输出到 stdout |

### 2. 切分文档 (doc_split.py)

将已有文本文件切分为 chunks：

```bash
# 文本切分（默认）
python agent/skills/yz-doc/scripts/doc_split.py input.md

# Markdown 按标题切分
python agent/skills/yz-doc/scripts/doc_split.py input.md --splitter markdown

# 自定义切片大小
python agent/skills/yz-doc/scripts/doc_split.py input.txt --chunk-size 500 --chunk-overlap 50

# 输出为 JSON
python agent/skills/yz-doc/scripts/doc_split.py input.md -o chunks.json --format json
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `source` | 是 | 文本文件路径 |
| `--splitter` | 否 | 切分策略：`text`（默认）或 `markdown` |
| `--chunk-size` | 否 | 切片大小，默认 1000 字符 |
| `--chunk-overlap` | 否 | 切片重叠，默认 200 字符 |
| `--format` | 否 | 输出格式：`text`（默认）或 `json` |
| `-o/--output` | 否 | 输出文件路径 |

### 3. 一站式处理 (doc_process.py)

加载 + 切分一步完成：

```bash
# 基本用法
python agent/skills/yz-doc/scripts/doc_process.py README.md

# 飞书 + Markdown切分
python agent/skills/yz-doc/scripts/doc_process.py "https://xxx.feishu.cn/wiki/xxx" \
  --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET \
  --splitter markdown --chunk-size 800

# 输出 JSON 到文件
python agent/skills/yz-doc/scripts/doc_process.py file.pdf -o chunks.json --format json
```

参数为 `doc_load.py` 和 `doc_split.py` 参数的合集。

## 支持的格式

| 格式 | 扩展名 | 来源 | 配置要求 |
|------|--------|------|---------|
| 文本 | .txt | 本地/URL | 无 |
| Markdown | .md | 本地/URL | 无 |
| Excel | .xlsx, .xls | 仅本地 | 无 |
| PDF | .pdf | 仅URL | 无 |
| Word | .doc, .docx | 仅URL | 无 |
| 图片 | .png, .jpg, .gif 等 | 仅URL | 无 |
| 飞书文档 | feishu.cn URL | 仅URL | app_id + app_secret |

## JSON 输出示例

**doc_load.py --format json：**

```json
{
  "doc_id": "doc_abc123",
  "content": "文档内容...",
  "doc_type": "markdown",
  "source": "README.md",
  "metadata": {"loader": "langchain"},
  "created_at": "2025-01-01T00:00:00"
}
```

**doc_split.py --format json：**

```json
[
  {
    "chunk_id": "chunk_abc123",
    "content": "切片内容...",
    "doc_id": "doc_abc123",
    "index": 0,
    "metadata": {"total_chunks": 5}
  }
]
```

## 注意事项

- PDF/Word/图片仅支持 URL，不支持本地文件（通过 AIGC API 解析）
- Excel 仅支持本地文件
- 飞书文档必须传入 `--app-id` 和 `--app-secret`，或设置环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`
- 其他格式无需任何配置，开箱即用
