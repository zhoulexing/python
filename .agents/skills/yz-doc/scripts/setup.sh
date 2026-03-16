#!/bin/bash
# 安装 yz-doc 及其依赖
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "=== 安装 yz-doc 依赖 ==="

# 安装本地 yz_dubbo 包（yz_doc 的依赖）
echo "安装 yz-dubbo..."
pip install -e "$PROJECT_ROOT/packages/yz_dubbo" --quiet

# 安装 yz_doc 及飞书扩展
echo "安装 yz-doc[feishu]..."
pip install -e "$PROJECT_ROOT/packages/yz_doc[feishu]" --quiet

# 安装 requirements.txt 中的额外依赖
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "安装额外依赖..."
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
fi

echo "=== 安装完成 ==="
