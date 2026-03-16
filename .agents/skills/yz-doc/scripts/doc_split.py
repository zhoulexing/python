#!/usr/bin/env python3
"""文档切分 CLI - 将文本文件切分为 chunks"""

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
from yz_doc.core.document import Document


def main():
    parser = argparse.ArgumentParser(
        description="将文本文件切分为 chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.md
  %(prog)s input.md --splitter markdown --chunk-size 500
  %(prog)s input.txt -o chunks.json --format json
        """,
    )
    parser.add_argument("source", help="文本文件路径")
    parser.add_argument("--splitter", choices=["text", "markdown"], default="text",
                        help="切分策略（默认: text）")
    parser.add_argument("--chunk-size", type=int, default=1000, help="切片大小（默认: 1000）")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="切片重叠（默认: 200）")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="输出格式（默认: text）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认输出到 stdout）")
    args = parser.parse_args()

    source_path = args.source
    if not os.path.isfile(source_path):
        print(f"错误: 文件不存在: {source_path}", file=sys.stderr)
        sys.exit(1)

    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = Document(content=content, source=source_path)

    try:
        chunks = YZDoc().split(
            doc,
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
