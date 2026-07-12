#!/usr/bin/env bash
set -euo pipefail

# Run all local validation YOLO detection experiments with n-size models.
# This is the resource-conscious set for local checks before running l-size
# formal experiments.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATION_DIR="${SCRIPT_DIR}/yolo_validation"

"${VALIDATION_DIR}/train_yolo11_pvel_ad.sh"
"${VALIDATION_DIR}/train_yolov8_pvel_ad.sh"
"${VALIDATION_DIR}/train_yolo11_pv_multi_defect.sh"
"${VALIDATION_DIR}/train_yolov8_pv_multi_defect.sh"
