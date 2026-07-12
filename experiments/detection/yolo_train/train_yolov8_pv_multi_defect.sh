#!/usr/bin/env bash
set -euo pipefail

# Full YOLOv8 baseline training entry point for the PV-Multi-Defect detection dataset.
# Override CONFIG to use another YAML file, or DEVICE to select CUDA, CPU, or
# Apple MPS without editing the YAML.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

CONFIG="${CONFIG:-${PROJECT_ROOT}/configs/detection/pv_multi_defect_yolov8l.yaml}"
DEVICE="${DEVICE:-}"

CMD=(
  python3 "${PROJECT_ROOT}/experiments/detection/run_yolo.py"
  train
  --config "${CONFIG}"
)

if [[ -n "${DEVICE}" ]]; then
  CMD+=(--device "${DEVICE}")
fi

"${CMD[@]}"
