#!/usr/bin/env bash
set -euo pipefail

# 意图：检查部署工具的命令行入口是否可解析。
# 这里不要求本机已有训练 checkpoint，因此只运行 help，避免伪造模型文件。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

python3 "${PROJECT_ROOT}/deployment/export_yolo.py" --help >/dev/null
python3 "${PROJECT_ROOT}/deployment/export_elpv.py" --help >/dev/null
