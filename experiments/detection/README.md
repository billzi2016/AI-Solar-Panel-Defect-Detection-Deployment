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

The shell scripts below run full training. They use the same processed dataset and the same wrapper, so the comparison focuses on the model version instead of different project logic.

YOLO11 default:

```bash
./experiments/detection/train_yolo11.sh
```

YOLOv8 baseline:

```bash
./experiments/detection/train_yolov8.sh
```

Both scripts accept environment overrides:

```bash
EPOCHS=50 BATCH=8 DEVICE=0 ./experiments/detection/train_yolo11.sh
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
