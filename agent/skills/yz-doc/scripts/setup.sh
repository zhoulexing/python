#!/bin/bash
# 安装 yz-doc 技能依赖（纯第三方包，无本地包依赖）
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 安装 yz-doc 技能依赖 ==="
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo "=== 安装完成 ==="
