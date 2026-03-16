#!/usr/bin/env python3
"""文档切分 CLI - 将文本文件切分为 chunks"""

import sys
import os
import json
import argparse

from lib import YZDoc
from lib.models import Document


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
    parser.add_argument("--splitter", choices=["text", "markdown"], default="text", help="切分策略（默认: text）")
    parser.add_argument("--chunk-size", type=int, default=1000, help="切片大小（默认: 1000）")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="切片重叠（默认: 200）")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式（默认: text）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    if not os.path.isfile(args.source):
        print(f"错误: 文件不存在: {args.source}", file=sys.stderr)
        sys.exit(1)

    with open(args.source, "r", encoding="utf-8") as f:
        content = f.read()

    doc = Document(content=content, source=args.source)

    try:
        chunks = YZDoc().split(doc, splitter_type=args.splitter, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = json.dumps([c.to_dict() for c in chunks], ensure_ascii=False, indent=2)
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
