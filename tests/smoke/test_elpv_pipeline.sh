#!/usr/bin/env bash
set -euo pipefail

# 意图：快速检查 ELPV 图像级实验入口是否能加载真实数据并完成短训练。
# 这个 smoke test 使用真实 ELPV 标签和图片跑 ResNet-18 一个 epoch，不使用 mock 数据。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

python3 "${PROJECT_ROOT}/experiments/elpv/run_torchvision.py" --help >/dev/null
python3 "${PROJECT_ROOT}/deployment/export_elpv.py" --help >/dev/null

test -f "${PROJECT_ROOT}/configs/elpv/resnet18_binary.yaml"
test -f "${PROJECT_ROOT}/configs/elpv/swin_t_binary.yaml"

python3 "${PROJECT_ROOT}/experiments/elpv/run_torchvision.py" \
  train \
  --config "${PROJECT_ROOT}/configs/elpv/resnet18_binary.yaml" \
  --epochs 1 \
  --batch 32 \
  --imgsz 224 \
  --device cpu \
  --name elpv_resnet18_binary_smoke >/dev/null

test -f "${PROJECT_ROOT}/outputs/elpv/elpv_resnet18_binary_smoke/best.pt"
test -f "${PROJECT_ROOT}/outputs/elpv/elpv_resnet18_binary_smoke/metrics.json"
