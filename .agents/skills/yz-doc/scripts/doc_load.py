#!/usr/bin/env python3
"""文档加载 CLI - 支持 txt/md/xlsx/pdf/docx/图片/飞书"""

import sys
import os
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
PACKAGES_DIR = os.path.join(PROJECT_ROOT, "packages")

for pkg in ["yz_doc", "yz_dubbo"]:
    pkg_path = os.path.join(PACKAGES_DIR, pkg)
    if os.path.isdir(pkg_path) and pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from yz_doc import YZDoc


def main():
    parser = argparse.ArgumentParser(
        description="加载文档并输出内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s README.md
  %(prog)s "https://xxx.feishu.cn/wiki/xxx" --app-id ID --app-secret SECRET
  %(prog)s file.pdf -o result.json --format json
        """,
    )
    parser.add_argument("source", help="文件路径或 URL")
    parser.add_argument("--app-id", help="飞书 App ID（或设置环境变量 FEISHU_APP_ID）")
    parser.add_argument("--app-secret", help="飞书 App Secret（或设置环境变量 FEISHU_APP_SECRET）")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text",
                        help="输出格式（默认: text）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认输出到 stdout）")
    args = parser.parse_args()

    config = {}
    app_id = args.app_id or os.getenv("FEISHU_APP_ID")
    app_secret = args.app_secret or os.getenv("FEISHU_APP_SECRET")
    if app_id and app_secret:
        config["feishu"] = {"app_id": app_id, "app_secret": app_secret}

    try:
        doc = YZDoc(config).load(args.source)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = json.dumps(doc.to_dict(), ensure_ascii=False, indent=2, default=str)
    elif args.format == "markdown":
        title = doc.metadata.get("title", doc.source)
        output = f"# {title}\n\n{doc.content}"
    else:
        output = doc.content

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
