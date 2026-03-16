#!/usr/bin/env python3
"""文档加载 CLI - 支持 txt/md/xlsx/pdf/docx/图片/飞书"""

import sys
import os
import json
import argparse

from lib import YZDoc


def main():
    parser = argparse.ArgumentParser(
        description="加载文档并输出内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s README.md
  %(prog)s "https://xxx.feishu.cn/wiki/xxx" --app-id ID --app-secret SECRET
  %(prog)s "https://xxx.feishu.cn/wiki/xxx" --app-id ID --app-secret SECRET --download-images --cdn-operator-id 123 --cdn-channel my_channel
  %(prog)s file.pdf -o result.json --format json
        """,
    )
    parser.add_argument("source", help="文件路径或 URL")

    g_feishu = parser.add_argument_group("飞书配置（飞书文档必填）")
    g_feishu.add_argument("--app-id", help="飞书 App ID（或环境变量 FEISHU_APP_ID）")
    g_feishu.add_argument("--app-secret", help="飞书 App Secret（或环境变量 FEISHU_APP_SECRET）")

    g_cdn = parser.add_argument_group("七牛云 CDN 配置（飞书图片上传，可选）")
    g_cdn.add_argument("--download-images", action="store_true", help="下载飞书文档中的图片并上传到七牛云")
    g_cdn.add_argument("--cdn-operator-id", type=int, help="七牛云操作员 ID")
    g_cdn.add_argument("--cdn-channel", help="七牛云业务渠道")
    g_cdn.add_argument("--cdn-operator-type", type=int, default=1, help="操作员类型（默认 1）")
    g_cdn.add_argument("--cdn-from-app", help="来源应用")
    g_cdn.add_argument("--cdn-max-size", type=int, help="最大文件大小（字节）")

    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="输出格式（默认: text）")
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
