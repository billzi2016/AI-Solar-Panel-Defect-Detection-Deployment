#!/usr/bin/env bash
set -euo pipefail

# Smoke check for the detection pipeline. This is intentionally short and should
# be used only to verify that data conversion and the Ultralytics wrapper run.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

python3 "${PROJECT_ROOT}/data_tools/converters/build_yolo_detection_dataset.py" --dataset pv_multi_defect

python3 "${PROJECT_ROOT}/experiments/detection/run_yolo.py" \
  train \
  --data "${PROJECT_ROOT}/datasets/processed/yolo/pv_multi_defect/dataset.yaml" \
  --model "${MODEL:-yolo11n.pt}" \
  --epochs 1 \
  --imgsz "${IMGSZ:-320}" \
  --batch "${BATCH:-4}" \
  --name "${NAME:-pv_multi_defect_smoke}"
