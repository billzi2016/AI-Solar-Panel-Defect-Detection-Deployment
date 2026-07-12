#!/usr/bin/env bash
set -euo pipefail

# 意图：运行 ELPV 的 ResNet-18 图像级实验组合。
# 这里不写模型逻辑，只把二分类和概率回归两个真实配置串起来，便于复现。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEVICE="${DEVICE:-}"

run_config() {
  local config_path="$1"
  local cmd=(
    python3 "${PROJECT_ROOT}/experiments/elpv/run_torchvision.py"
    train
    --config "${PROJECT_ROOT}/${config_path}"
  )

  if [[ -n "${DEVICE}" ]]; then
    cmd+=(--device "${DEVICE}")
  fi
  "${cmd[@]}"
}

run_config "configs/elpv/resnet18_binary.yaml"
run_config "configs/elpv/resnet18_regression.yaml"
