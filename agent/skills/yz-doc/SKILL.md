---
name: yz-doc
description: 多格式文档加载与智能切分工具。支持 txt、md、xlsx、pdf、docx、图片、飞书文档的加载，以及 text/markdown 两种切分策略。当需要读取文档内容、解析飞书文档、将长文本切分为 chunks 时使用此技能。触发词包括"加载文档"、"解析文档"、"读取飞书"、"文档切分"、"文本分块"等。
---

# YZ-Doc 文档处理

自包含技能，核心代码位于 `scripts/lib/`，仅依赖第三方 pip 包（httpx、lark-oapi、langchain 等），无 yz-doc / yz-dubbo 本地包依赖。

## 环境准备

```bash
bash agent/skills/yz-doc/scripts/setup.sh
```

## 命令列表

**所有命令必须在项目根目录下，从 `agent/skills/yz-doc/scripts/` 目录执行：**

```bash
cd agent/skills/yz-doc/scripts
```

### 1. 加载文档 (doc_load.py)

```bash
# 本地文件（无需任何配置）
python doc_load.py README.md
python doc_load.py data.xlsx

# 远程文件（PDF/Word/图片，需为 URL）
python doc_load.py "https://example.com/file.pdf"

# 飞书文档（必须提供 app_id + app_secret）
python doc_load.py "https://xxx.feishu.cn/wiki/xxx" \
  --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET

# 飞书文档 + 图片上传七牛云（需额外 CDN 配置，见下方说明）
python doc_load.py "https://xxx.feishu.cn/wiki/xxx" \
  --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET \
  --download-images --cdn-operator-id 12345 --cdn-channel my_channel

# 输出到文件
python doc_load.py file.md -o result.json --format json
```

### 2. 切分文档 (doc_split.py)

```bash
python doc_split.py input.md
python doc_split.py input.md --splitter markdown --chunk-size 500
python doc_split.py input.txt -o chunks.json --format json
```

### 3. 一站式处理 (doc_process.py)

```bash
python doc_process.py README.md
python doc_process.py "https://xxx.feishu.cn/wiki/xxx" \
  --app-id ID --app-secret SECRET --splitter markdown --chunk-size 800
```

## 配置要求一览

| 格式 | 来源 | 必填配置 | 可选配置 |
|------|------|---------|---------|
| txt / md | 本地或URL | 无 | 无 |
| xlsx | 仅本地 | 无 | 无 |
| pdf / docx / 图片 | 仅URL | 无 | 无 |
| 飞书文档（纯文本） | feishu.cn URL | `--app-id` + `--app-secret` | 无 |
| 飞书文档（含图片上传） | feishu.cn URL | `--app-id` + `--app-secret` + CDN 配置 | 见下方 |

## 飞书配置

飞书文档加载**必须**提供以下两个参数（二选一方式传入）：

| 参数 | CLI 参数 | 环境变量 |
|------|---------|---------|
| 应用 ID | `--app-id` | `FEISHU_APP_ID` |
| 应用密钥 | `--app-secret` | `FEISHU_APP_SECRET` |

## 七牛云 CDN 配置（可选）

**仅当需要将飞书文档中的图片下载并上传到七牛云 CDN 时才需要。** 不配置时，飞书文档中的图片保留为原始 token 引用。

### 触发条件

加载飞书文档时传入 `--download-images` 标志。

### 依赖链路

```
FeishuLoader (download_images=True)
  → 下载图片 (飞书 API)
  → 获取上传 Token (Dubbo RPC → Tether 网关)
  → 上传到七牛云 (httpx → upload.qiniup.com)
  → 替换 Markdown 中的图片链接
```

### 所需参数

| CLI 参数 | 必填 | 说明 |
|---------|------|------|
| `--download-images` | 是 | 开启图片下载+上传 |
| `--cdn-operator-id` | 是 | 操作员 ID |
| `--cdn-channel` | 是 | 业务渠道 |
| `--cdn-operator-type` | 否 | 操作员类型，默认 1 |
| `--cdn-from-app` | 否 | 来源应用 |
| `--cdn-max-size` | 否 | 最大文件大小（字节） |

### 网络依赖

七牛云上传还依赖以下内网服务（根据环境变量 `APPLICATION_STANDARD_ENV` 自动选择 qa/pre/prod）：

- **Tether 网关**（Dubbo RPC）：获取七牛云上传 Token
- **静态代理服务**：代理上传请求到七牛云

## 目录结构

```
scripts/
├── doc_load.py          # CLI: 加载文档
├── doc_split.py         # CLI: 切分文档
├── doc_process.py       # CLI: 加载+切分
├── requirements.txt     # 第三方依赖
├── setup.sh             # 安装依赖
└── lib/                 # 核心库（自包含）
    ├── __init__.py      # YZDoc 入口类
    ├── models.py        # Document + Chunk + 异常
    ├── loaders/         # 文档加载器
    │   ├── feishu.py    # 飞书加载器
    │   ├── aigc.py      # AIGC加载器(PDF/Word/图片)
    │   └── langchain.py # LangChain加载器(txt/md/xlsx)
    ├── splitters/       # 文档切分器
    │   ├── text.py      # 文本切分
    │   └── markdown.py  # Markdown按标题切分
    └── utils/
        ├── dubbo_client.py  # Dubbo RPC 客户端
        ├── feishu_client.py # 飞书 API 客户端
        ├── qiniu.py         # 七牛云上传
        └── env.py           # 环境路由
```
