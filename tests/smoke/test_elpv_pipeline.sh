#!/usr/bin/env bash
set -euo pipefail

# 意图：快速检查 ELPV 图像级实验入口是否能加载依赖和配置。
# 这个 smoke test 不训练模型，只验证命令行入口、配置文件和导出脚本 help。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

python3 "${PROJECT_ROOT}/experiments/elpv/run_torchvision.py" --help >/dev/null
python3 "${PROJECT_ROOT}/deployment/export_elpv.py" --help >/dev/null

test -f "${PROJECT_ROOT}/configs/elpv/resnet18_binary.yaml"
test -f "${PROJECT_ROOT}/configs/elpv/swin_t_binary.yaml"
