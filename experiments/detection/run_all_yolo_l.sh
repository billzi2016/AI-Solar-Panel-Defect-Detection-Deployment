#!/usr/bin/env bash
set -euo pipefail

# Run all formal large-model YOLO detection experiments.
# These scripts use the l-size configs by default. Override DEVICE from the
# shell when running on CUDA, MPS, or CPU.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/yolo_train/train_yolo11_pvel_ad.sh"
"${SCRIPT_DIR}/yolo_train/train_yolov8_pvel_ad.sh"
"${SCRIPT_DIR}/yolo_train/train_yolo11_pv_multi_defect.sh"
"${SCRIPT_DIR}/yolo_train/train_yolov8_pv_multi_defect.sh"
