#!/usr/bin/env bash
set -euo pipefail

# 意图：运行 ELPV 的 Swin-T 图像级实验组合。
# Swin-T 比 ResNet-18 更重，适合在资源允许时评估全局上下文建模能力。

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

run_config "configs/elpv/swin_t_binary.yaml"
run_config "configs/elpv/swin_t_regression.yaml"
