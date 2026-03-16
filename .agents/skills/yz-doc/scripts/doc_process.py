#!/usr/bin/env python3
"""一站式文档处理 CLI - 加载 + 切分"""

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
        description="一站式文档处理：加载 + 切分",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s README.md
  %(prog)s "https://xxx.feishu.cn/wiki/xxx" --app-id ID --app-secret SECRET
  %(prog)s file.md --splitter markdown --chunk-size 800 -o chunks.json --format json
        """,
    )
    parser.add_argument("source", help="文件路径或 URL")
    parser.add_argument("--app-id", help="飞书 App ID（或设置环境变量 FEISHU_APP_ID）")
    parser.add_argument("--app-secret", help="飞书 App Secret（或设置环境变量 FEISHU_APP_SECRET）")
    parser.add_argument("--splitter", choices=["text", "markdown"], default="text",
                        help="切分策略（默认: text）")
    parser.add_argument("--chunk-size", type=int, default=1000, help="切片大小（默认: 1000）")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="切片重叠（默认: 200）")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="输出格式（默认: text）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认输出到 stdout）")
    args = parser.parse_args()

    config = {}
    app_id = args.app_id or os.getenv("FEISHU_APP_ID")
    app_secret = args.app_secret or os.getenv("FEISHU_APP_SECRET")
    if app_id and app_secret:
        config["feishu"] = {"app_id": app_id, "app_secret": app_secret}

    try:
        chunks = YZDoc(config).process(
            args.source,
            splitter_type=args.splitter,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = json.dumps(
            [c.to_dict() for c in chunks], ensure_ascii=False, indent=2
        )
    else:
        lines = []
        for c in chunks:
            lines.append(f"--- Chunk {c.index} ({len(c.content)} chars) ---")
            lines.append(c.content)
            lines.append("")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已保存到: {args.output}（共 {len(chunks)} 个切片）", file=sys.stderr)
    else:
        print(output)
        print(f"\n共 {len(chunks)} 个切片", file=sys.stderr)


if __name__ == "__main__":
    main()
