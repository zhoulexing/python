#!/usr/bin/env python3
"""一站式文档处理 CLI - 加载 + 切分"""

import sys
import os
import json
import argparse

from lib import YZDoc


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

    g_feishu = parser.add_argument_group("飞书配置")
    g_feishu.add_argument("--app-id", help="飞书 App ID（或环境变量 FEISHU_APP_ID）")
    g_feishu.add_argument("--app-secret", help="飞书 App Secret（或环境变量 FEISHU_APP_SECRET）")

    g_cdn = parser.add_argument_group("七牛云 CDN 配置（可选）")
    g_cdn.add_argument("--download-images", action="store_true", help="下载飞书图片并上传七牛云")
    g_cdn.add_argument("--cdn-operator-id", type=int, help="操作员 ID")
    g_cdn.add_argument("--cdn-channel", help="业务渠道")
    g_cdn.add_argument("--cdn-operator-type", type=int, default=1, help="操作员类型（默认 1）")
    g_cdn.add_argument("--cdn-from-app", help="来源应用")
    g_cdn.add_argument("--cdn-max-size", type=int, help="最大文件大小（字节）")

    parser.add_argument("--splitter", choices=["text", "markdown"], default="text", help="切分策略（默认: text）")
    parser.add_argument("--chunk-size", type=int, default=1000, help="切片大小（默认: 1000）")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="切片重叠（默认: 200）")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式（默认: text）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    config = {}
    app_id = args.app_id or os.getenv("FEISHU_APP_ID")
    app_secret = args.app_secret or os.getenv("FEISHU_APP_SECRET")
    if app_id and app_secret:
        feishu_cfg = {"app_id": app_id, "app_secret": app_secret}
        if args.download_images:
            feishu_cfg["download_images"] = True
            feishu_cfg["cdn"] = {
                "operator_id": args.cdn_operator_id,
                "channel": args.cdn_channel,
                "operator_type": args.cdn_operator_type,
                "from_app": args.cdn_from_app,
                "max_size": args.cdn_max_size,
            }
        config["feishu"] = feishu_cfg

    try:
        chunks = YZDoc(config).process(
            args.source, splitter_type=args.splitter, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap
        )
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
