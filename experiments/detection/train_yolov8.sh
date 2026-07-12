#!/usr/bin/env bash
set -euo pipefail

# Full YOLOv8 baseline training entry point for the PVEL-AD detection dataset.
# Override EPOCHS, IMGSZ, BATCH, DEVICE, DATASET_YAML, or MODEL from the shell
# when running on a different machine or GPU.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DATASET_YAML="${DATASET_YAML:-${PROJECT_ROOT}/datasets/processed/yolo/pvel_ad/dataset.yaml}"
MODEL="${MODEL:-yolov8n.pt}"
EPOCHS="${EPOCHS:-100}"
IMGSZ="${IMGSZ:-640}"
BATCH="${BATCH:-16}"
DEVICE="${DEVICE:-}"
NAME="${NAME:-pvel_ad_yolov8n}"

CMD=(
  python3 "${PROJECT_ROOT}/experiments/detection/run_yolo.py"
  train
  --data "${DATASET_YAML}"
  --model "${MODEL}"
  --epochs "${EPOCHS}"
  --imgsz "${IMGSZ}"
  --batch "${BATCH}"
  --name "${NAME}"
)

if [[ -n "${DEVICE}" ]]; then
  CMD+=(--device "${DEVICE}")
fi

"${CMD[@]}"
