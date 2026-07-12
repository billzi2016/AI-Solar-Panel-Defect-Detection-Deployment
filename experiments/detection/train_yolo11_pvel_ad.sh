#!/usr/bin/env bash
set -euo pipefail

# Full YOLO11 training entry point. It fine-tunes on PVEL-AD by default.
# Override EPOCHS, IMGSZ, BATCH, DEVICE, DATASET_YAML, or MODEL from the shell
# when running on a different dataset, machine, GPU, or Apple MPS backend.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DATASET_YAML="${DATASET_YAML:-${PROJECT_ROOT}/datasets/processed/yolo/pvel_ad/dataset.yaml}"
MODEL="${MODEL:-yolo11n.pt}"
EPOCHS="${EPOCHS:-100}"
IMGSZ="${IMGSZ:-640}"
BATCH="${BATCH:-16}"
DEVICE="${DEVICE:-}"
NAME="${NAME:-pvel_ad_yolo11n}"

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
