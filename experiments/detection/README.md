# Detection Experiments

This directory contains experiment entry points for object detection. The project uses Ultralytics YOLO for model training, validation, prediction, and export. The local code prepares datasets and calls the library; it does not implement a custom detector.

## Workflow

1. Convert a downloaded VOC-style dataset to YOLO layout.
2. Run the YOLO11 training entry point as the current default experiment.
3. Run the YOLOv8 baseline with the same processed dataset.
4. Validate the trained checkpoint.
5. Export the checkpoint to ONNX for deployment checks.

## Prepare Data

PVEL-AD:

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
```

PV-Multi-Defect:

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

## Full Training

The shell scripts below run full training. They use the same wrapper, so the comparison focuses on the dataset and model version instead of different project logic.

## Training Matrix

| Dataset | YOLO11 | YOLOv8 |
|---|---|---|
| PVEL-AD | `./experiments/detection/train_yolo11_pvel_ad.sh` | `./experiments/detection/train_yolov8_pvel_ad.sh` |
| PV-Multi-Defect | `./experiments/detection/train_yolo11_pv_multi_defect.sh` | `./experiments/detection/train_yolov8_pv_multi_defect.sh` |

The scripts above use `l` configs for formal training. The complete `n/s/m/l/x` matrix is documented in `train.md`. Local validation scripts use `n` configs and live in `experiments/detection/yolo_validation/`.

PVEL-AD with YOLO11:

```bash
./experiments/detection/train_yolo11_pvel_ad.sh
```

PV-Multi-Defect with YOLO11:

```bash
./experiments/detection/train_yolo11_pv_multi_defect.sh
```

Both scripts accept environment overrides:

```bash
EPOCHS=50 BATCH=8 DEVICE=0 ./experiments/detection/train_yolo11_pvel_ad.sh
```

Apple Silicon can use MPS:

```bash
DEVICE=mps ./experiments/detection/train_yolo11_pvel_ad.sh
```

Use PV-Multi-Defect with its matching entry point:

```bash
./experiments/detection/train_yolo11_pv_multi_defect.sh
```

## Smoke Check

Smoke checks live under `tests/smoke/` because they are test utilities, not full experiments.

```bash
./tests/smoke/test_yolo_detection_pipeline.sh
```

## Validation

```bash
python3 experiments/detection/run_yolo.py val --data datasets/processed/yolo/pvel_ad/dataset.yaml --model outputs/detection/pvel_ad_yolo11n/weights/best.pt
```

## Export

```bash
python3 experiments/detection/run_yolo.py export --model outputs/detection/pvel_ad_yolo11n/weights/best.pt --format onnx
```

Outputs are written under `outputs/detection/`, which is ignored by git.
